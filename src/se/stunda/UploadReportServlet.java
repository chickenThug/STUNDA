package se.stunda;

import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.nio.file.*;

public class UploadReportServlet extends HttpServlet {
    private static final String LOG_FILE_PATH = "/var/lib/stunda/report_data/report_data.txt";

    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        try {

            // Get the data from the request
            String sweLemma          = request.getParameter("sweLemma");
            String engLemma          = request.getParameter("engLemma");
            boolean nonComputingTerm = Boolean.parseBoolean(request.getParameter("nonComputingTerm"));
            boolean wrongTranslation = Boolean.parseBoolean(request.getParameter("wrongTranslation"));
            boolean inappropiate     = Boolean.parseBoolean(request.getParameter("inappropiate"));
            String other             = request.getParameter("other");
            String timestamp         = request.getParameter("timestamp");

            // Format report string
            String report = String.format("Swedish Lemma: %s, English Lemma: %s, Non-Computing Term: %b, Wrong Translation: %b, Inappropriate: %b, Other: %s, Timestamp: %s",
                sweLemma,
                engLemma,
                nonComputingTerm,
                wrongTranslation,
                inappropiate,
                other,
                timestamp
            );

            // Ensure the directory exists
            Path logFilePath = Paths.get(LOG_FILE_PATH);
            Path parentDir = logFilePath.getParent();
            if (!Files.exists(parentDir)) {
                Files.createDirectories(parentDir);
            }

            // Append the report at the end of file
            Files.write(Paths.get(LOG_FILE_PATH), report.getBytes(), StandardOpenOption.CREATE, StandardOpenOption.APPEND);

            // Send back a response
            response.setContentType("text/plain");
            response.getWriter().write("Report Successful");
        } catch (Exception e) {
            // Send back an error response with the error message
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("text/plain");
            response.getWriter().write("error: " + e.getMessage());
        }

    }
}

