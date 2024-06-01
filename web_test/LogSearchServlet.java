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
            String logMessage = "Button was pressed!\n";  // Log message to append

            // Using Java NIO to append text to a file in a thread-safe manner
            Files.write(Paths.get(LOG_FILE_PATH), logMessage.getBytes(), StandardOpenOption.CREATE, StandardOpenOption.APPEND);

            // Send back a response
            response.setContentType("text/plain");
            response.getWriter().write("Search Logged Successfully");
        } catch (Exception e) {
            // Send back an error response
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("text/plain");
            response.getWriter().write(e.getMessage());
        }
    }
}