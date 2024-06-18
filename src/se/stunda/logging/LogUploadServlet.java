package se.stunda.logging;

import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

public class LogUploadServlet extends HttpServlet {
    private static final String LOG_FILE_PATH = "/var/log/stunda/log_upload.txt";

    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        try {
            String timestamp = request.getParameter("timestamp");
            String uploadType = request.getParameter("uploadType");
            boolean successful = Boolean.parseBoolean(request.getParameter("successful"));

            String logMessage = String.format("Time Stamp: %s, Upload Type: %s, Successful: %s\n",
                    timestamp,
                    uploadType,
                    successful);

            Files.write(Paths.get(LOG_FILE_PATH), logMessage.getBytes(), StandardOpenOption.CREATE,
                    StandardOpenOption.APPEND);

            response.setContentType("text/plain");
            response.getWriter().write("Upload Logged Successfully");
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("text/plain");
            response.getWriter().write("error: " + e.getMessage());
        }

    }

}
