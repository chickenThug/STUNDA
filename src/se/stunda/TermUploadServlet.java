package se.stunda;

import javax.servlet.annotation.MultipartConfig;
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.charset.Charset;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.file.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@MultipartConfig
public class TermUploadServlet extends HttpServlet {
    private static final String FILE_PATH = Config.DATA_DIR + "/terms/unprocessed.csv";

    private static String csvQuote(String field) {
        if (field != null && field.contains(",") && !field.startsWith("\"")) {
            return "\"" + field + "\"";
        }
        return field;
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

                    try (BufferedReader reader = new BufferedReader(
                            new InputStreamReader(new ByteArrayInputStream(rawBytes), detectedCharset))) {
                        String line;
                        int i = 0;
                        Pattern pattern = null;

                        while ((line = reader.readLine()) != null) {
                            // Strip UTF-8 BOM if present (common in Excel-generated CSV files)
                            if (i == 0 && line.startsWith("\uFEFF")) {
                                line = line.substring(1);
                            }

                            //CSV header
                            if (i == 0) {
                                i++;
                                //Proccess , seperated csv
                                if (line.equals("eng_term,swe_term") || line.equals("eng_term,swe_term,source")) {
                                    // Regex to match CSV fields that may contain commas within quotes
                                    pattern = Pattern.compile("(\"[^\"]*\"|[^,]+)");
                                    continue;
                                }
                                //Proccess ; seperated csv
                                else if (line.equals("eng_term;swe_term") || line.equals("eng_term;swe_term;source")) {
                                    // Regex to match CSV fields that may contain commas within quotes
                                    pattern = Pattern.compile("(\"[^\"]*\"|[^;]+)");
                                    continue;
                                }
                                // No recognized header - treat first line as data and auto-detect delimiter
                                else {
                                    if (line.contains(";")) {
                                        pattern = Pattern.compile("(\"[^\"]*\"|[^;]+)");
                                    } else {
                                        pattern = Pattern.compile("(\"[^\"]*\"|[^,]+)");
                                    }
                                    // Fall through to process this line as data
                                }
                            }
                            //Match regex
                            Matcher matcher = pattern.matcher(line);
                            String[] parts = new String[4];
                            int index = 0;

                            // Match the first four entries
                            while (matcher.find()) {
                                if (index < 4) {
                                    // Check if group 1 (quoted value) is not null, otherwise use group 2
                                    parts[index++] = matcher.group(1) != null ? matcher.group(1) : matcher.group(2);
                                }
                            }

                            if (index >= 2) {
                                String rowSource = (index >= 3) ? parts[2] : source;
                                String rowComment = (index >= 4 && parts[3] != null) ? parts[3] : "";
                                String writeString = csvQuote(parts[0]) + "," + csvQuote(parts[1]) + "," + csvQuote(rowSource) + "," + csvQuote(rowComment) + "\n";
                                Files.write(Paths.get(FILE_PATH), writeString.getBytes("utf-8"), StandardOpenOption.CREATE,
                                    StandardOpenOption.APPEND);
                            }
                            else {
                                //invalid CSV line
                            }
                            
                        }
                    }
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