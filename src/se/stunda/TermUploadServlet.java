package se.stunda;

import javax.servlet.annotation.MultipartConfig;
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.nio.file.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@MultipartConfig
public class TermUploadServlet extends HttpServlet {
    private static final String FILE_PATH = "/var/lib/stunda/terms/unprocessed.csv";

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
                    try (BufferedReader reader = new BufferedReader(new InputStreamReader(filePart.getInputStream()))) {
                        String line;
                        int i = 0;
                        Pattern pattern = null;

                        while ((line = reader.readLine()) != null) {
                            //CSV header
                            if (i == 0) {
                                i++;
                                //Proccess , seperated csv
                                if (line.equals("eng_term,swe_term")) {
                                    // Regex to match CSV fields that may contain commas within quotes
                                    pattern = Pattern.compile("(\"[^\"]*\"|[^,]+)");
                                    continue;
                                }
                                //Proccess ; seperated csv
                                else if (line.equals("eng_term;swe_term")) {
                                    // Regex to match CSV fields that may contain commas within quotes
                                    pattern = Pattern.compile("(\"[^\"]*\"|[^;]+)");
                                    continue;
                                }
                                //Incorrect CSV header
                                else  {
                                    response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
                                    response.setContentType("text/plain");
                                    response.getWriter().write("Invalid CSV header");
                                    break;
                                }
                            }
                            //Match regex
                            Matcher matcher = pattern.matcher(line);
                            String[] parts = new String[2];
                            int index = 0;

                            // Match the first two entries
                            while (matcher.find()) {
                                if (index < 2) {
                                    // Check if group 1 (quoted value) is not null, otherwise use group 2
                                    parts[index++] = matcher.group(1) != null ? matcher.group(1) : matcher.group(2);
                                }
                            }
                            
                            if (index == 2) {
                                String writeString = parts[0] + "," + parts[1] + "," + source + "\n";
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