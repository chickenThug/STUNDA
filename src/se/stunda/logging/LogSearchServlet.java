package se.stunda.logging;

import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import com.fasterxml.jackson.databind.ObjectMapper;

public class LogSearchServlet extends HttpServlet {
    private static final String LOG_FILE_PATH = "/var/log/stunda/log_search.txt";
    private static final ObjectMapper mapper = new ObjectMapper();

    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        try {

            // Read the request body
            StringBuilder requestBody = new StringBuilder();
            String line;

            while ((line = request.getReader().readLine()) != null) {
                requestBody.append(line);
            }

            LogEntry logEntry = mapper.readValue(requestBody.toString(), LogEntry.class);

            String logMessage = String.format("Search String: %s, Search Hits: %d, Successful: %s, Time Stamp: %s, Search Language: %s\n",
                    logEntry.getSearchString(),
                    logEntry.getSearchHits(),
                    logEntry.getSuccessful(),
                    logEntry.getTimeStamp(),
                    logEntry.getSearchLanguage());

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

    static class LogEntry {
        private String searchString;
        private int searchHits;
        private Boolean successful;
        private String timeStamp;
        private String searchLanguage;

        // Getter for searchString
        public String getSearchString() {
            return searchString;
        }

        // Setter for searchString
        public void setSearchString(String searchString) {
            this.searchString = searchString;
        }

        // Getter for searchHits
        public int getSearchHits() {
            return searchHits;
        }

        // Setter for searchHits
        public void setSearchHits(int searchHits) {
            this.searchHits = searchHits;
        }

        // Getter for successful
        public Boolean getSuccessful() {
            return successful;
        }

        // Setter for successful
        public void setSuccessful(Boolean successful) {
            this.successful = successful;
        }

        // Getter for timeStamp
        public String getTimeStamp() {
            return timeStamp;
        }

        // Setter for timeStamp
        public void setTimeStamp(String timeStamp) {
            this.timeStamp = timeStamp;
        }

        // Getter for searchString
        public String getSearchLanguage() {
            return searchLanguage;
        }

        // Setter for searchString
        public void setSearchLanguage(String searchLanguage) {
            this.searchLanguage = searchLanguage;
        }
    }
}

