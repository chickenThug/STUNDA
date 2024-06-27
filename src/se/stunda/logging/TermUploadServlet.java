package se.stunda.logging;

import javax.servlet.annotation.MultipartConfig;
import javax.servlet.annotation.WebServlet;
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.nio.file.*;

@MultipartConfig
public class TermUploadServlet extends HttpServlet {
    private static final String FILE_PATH = "/var/lib/stunda/terms_test/unprocessed.csv";

    private static final String TERM_PATH = "/var/lib/stunda/terms";
    private static final String REPORT_PATH = "/var/lib/stunda/report_data";

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        try {
            response.setContentType("text/html;charset=UTF-8");

            deleteDirectory(TERM_PATH);
            deleteDirectory(REPORT_PATH);

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
                String source = request.getParameter("source");

                if (filePart != null) {
                    try (BufferedReader reader = new BufferedReader(new InputStreamReader(filePart.getInputStream()))) {
                        String line;
                        int i = 0;
                        while ((line = reader.readLine()) != null) {
                            if (i == 0) {
                                i++;
                                continue;
                            }
                            String writeString = line + "," + source + "\n";
                            Files.write(Paths.get(FILE_PATH), writeString.getBytes(), StandardOpenOption.CREATE,
                                    StandardOpenOption.APPEND);
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

    private void deleteDirectory(Path path) throws IOException {
        Files.walkFileTree(path, new SimpleFileVisitor<Path>() {
            @Override
            public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
                Files.delete(file);
                return FileVisitResult.CONTINUE;
            }

            @Override
            public FileVisitResult postVisitDirectory(Path dir, IOException exc) throws IOException {
                Files.delete(dir);
                return FileVisitResult.CONTINUE;
            }
        });
}