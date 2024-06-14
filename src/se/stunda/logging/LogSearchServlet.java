package se.stunda.logging;

import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

public class LogSearchServlet extends HttpServlet {
    private static final String LOG_FILE_PATH = "/var/log/stunda/log_search.txt";

    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        try {

            // Get the data from the request
            String searchString = request.getParameter("searchString");
            int searchHits = Integer.parseInt(request.getParameter("searchHits"));
            boolean successful = Boolean.parseBoolean(request.getParameter("successful"));
            String timestamp = request.getParameter("timestamp");
            String searchLanguage = request.getParameter("searchLanguage");

            String logMessage = String.format("Search String: %s, Search Hits: %d, Successful: %s, Time Stamp: %s, Search Language: %s\n",
                    searchString,
                    searchHits,
                    successful,
                    timestamp,
                    searchLanguage);

            // Using Java NIO to append text to a file in a thread-safe manner
            Files.write(Paths.get(LOG_FILE_PATH), logMessage.getBytes(), StandardOpenOption.CREATE, StandardOpenOption.APPEND);

            // Send back a response
            response.setContentType("text/plain");
            response.getWriter().write("Search Logged Successfully");
        } catch (Exception e) {
            // Send back an error response with the error message
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("text/plain");
            response.getWriter().write("error: " + e.getMessage());
        }

    }
}

