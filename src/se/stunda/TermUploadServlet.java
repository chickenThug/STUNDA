package se.stunda;

import com.opencsv.CSVParserBuilder;
import com.opencsv.CSVReader;
import com.opencsv.CSVReaderBuilder;
import com.opencsv.CSVWriter;
import javax.servlet.annotation.MultipartConfig;
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.charset.Charset;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.file.*;
import java.util.ArrayList;
import java.util.List;

@MultipartConfig
public class TermUploadServlet extends HttpServlet {
    private static final String FILE_PATH = Config.DATA_DIR + "/terms/unprocessed.csv";

    private static String stripSurroundingQuotes(String s) {
        if (s.length() >= 2 && s.charAt(0) == '"' && s.charAt(s.length() - 1) == '"') {
            return s.substring(1, s.length() - 1);
        }
        return s;
    }

    private static String clean(String s) {
        return stripSurroundingQuotes(s.trim());
    }

    private static List<String[]> expandRows(String eng, String swe, String src, String comment) {
        String[] engParts = eng.split(";", -1);
        String[] sweParts = swe.split(";", -1);
        boolean engHasSemi = engParts.length > 1;
        boolean sweHasSemi = sweParts.length > 1;

        List<String[]> rows = new ArrayList<>();

        if (engHasSemi && sweHasSemi) {
            if (engParts.length != sweParts.length) {
                System.err.println("Warning: mismatched semicolon count in eng_lemma (" +
                        eng + ") and swe_lemma (" + swe + ") — skipping split");
                rows.add(new String[]{clean(eng), clean(swe), src, comment});
            } else {
                for (int i = 0; i < engParts.length; i++) {
                    rows.add(new String[]{clean(engParts[i]), clean(sweParts[i]), src, comment});
                }
            }
        } else if (sweHasSemi) {
            for (String swePart : sweParts) {
                rows.add(new String[]{clean(eng), clean(swePart), src, comment});
            }
        } else if (engHasSemi) {
            for (String engPart : engParts) {
                rows.add(new String[]{clean(engPart), clean(swe), src, comment});
            }
        } else {
            rows.add(new String[]{clean(eng), clean(swe), src, comment});
        }

        return rows;
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        try {
            response.setContentType("text/html;charset=UTF-8");

            Path logFilePath = Paths.get(FILE_PATH);
            Path parentDir = logFilePath.getParent();
            if (!Files.exists(parentDir)) {
                Files.createDirectories(parentDir);
            }

            // Check if we have a file upload request
            if (request.getContentType() != null
                    && request.getContentType().toLowerCase().contains("multipart/form-data")) {
                // Get the part of the request that contains the file
                Part filePart = request.getPart("csvfile");
                // Get the provided source
                String source = request.getParameter("source"); 

                if (filePart != null) {
                    int termCount = 0;
                    // Read raw bytes and detect encoding (UTF-8 or ISO-8859-1)
                    ByteArrayOutputStream buffer = new ByteArrayOutputStream();
                    byte[] chunk = new byte[4096];
                    int bytesRead;
                    InputStream rawStream = filePart.getInputStream();
                    while ((bytesRead = rawStream.read(chunk)) != -1) {
                        buffer.write(chunk, 0, bytesRead);
                    }
                    byte[] rawBytes = buffer.toByteArray();

                    String detectedCharset = "UTF-8";
                    try {
                        Charset.forName("UTF-8")
                            .newDecoder()
                            .onMalformedInput(CodingErrorAction.REPORT)
                            .onUnmappableCharacter(CodingErrorAction.REPORT)
                            .decode(ByteBuffer.wrap(rawBytes));
                    } catch (CharacterCodingException e) {
                        detectedCharset = "ISO-8859-1";
                    }

                    // Strip UTF-8 BOM if present (common in Excel-generated CSV files)
                    String content = new String(rawBytes, detectedCharset);
                    if (content.startsWith("\uFEFF")) {
                        content = content.substring(1);
                    }

                    // Auto-detect delimiter from first line
                    char delimiter = content.contains(";") && !content.contains(",") ? ';' : ',';

                    try (CSVReader csvReader = new CSVReaderBuilder(new StringReader(content))
                            .withCSVParser(new CSVParserBuilder().withSeparator(delimiter).build())
                            .build();
                         CSVWriter csvWriter = new CSVWriter(new FileWriter(FILE_PATH, true),
                            CSVWriter.DEFAULT_SEPARATOR,
                            CSVWriter.DEFAULT_QUOTE_CHARACTER,
                            CSVWriter.DEFAULT_ESCAPE_CHARACTER,
                            CSVWriter.DEFAULT_LINE_END)) {

                        String[] parts;
                        boolean firstLine = true;

                        while ((parts = csvReader.readNext()) != null) {
                            // Skip recognized header rows
                            if (firstLine) {
                                firstLine = false;
                                if (parts.length >= 2 &&
                                        (parts[0].equals("eng_term") || parts[0].equals("eng_lemma")) &&
                                        (parts[1].equals("swe_term") || parts[1].equals("swe_lemma"))) {
                                    continue;
                                }
                            }

                            if (parts.length >= 2 && !parts[0].isEmpty() && !parts[1].isEmpty()) {
                                String rowSource = (parts.length >= 3 && !parts[2].isEmpty()) ? parts[2] : source;
                                String rowComment = (parts.length >= 4 && parts[3] != null) ? parts[3] : "";
                                for (String[] row : expandRows(parts[0], parts[1], rowSource, rowComment)) {
                                    csvWriter.writeNext(row);
                                    termCount++;
                                }
                            }
                        }
                    }
                    response.getWriter().write(String.valueOf(termCount));
                } else {
                    response.getWriter().println("No file uploaded!");
                }
            } else {
                response.getWriter().println("Invalid request content type!");
            }
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("text/plain");
            response.getWriter().write("error: " + e.getMessage());
        }

    }
}