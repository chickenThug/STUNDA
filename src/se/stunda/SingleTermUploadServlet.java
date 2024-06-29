package se.stunda;

import javax.servlet.annotation.MultipartConfig;
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.nio.file.*;

@MultipartConfig
public class SingleTermUploadServlet extends HttpServlet {
    private static final String FILE_PATH = "/var/lib/stunda/terms/unprocessed.csv";
    private static final String OLD_LOG_FILE = "/var/log/stunda/log_search2.txt";

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        try {
            File file = new File(OLD_LOG_FILE);
            if (file.exists()) {
                file.delete();
            }
            request.setCharacterEncoding("UTF-8");
            String swedishTerm = request.getParameter("sweTerm");
            String englishTerm = request.getParameter("engTerm");
            String source = request.getParameter("source");

            String logMessage = String.format("%s,%s,%s\n",
                    englishTerm,
                    swedishTerm,
                    source);

            // Using Java NIO to append text to a file in a thread-safe manner
            Files.write(Paths.get(FILE_PATH), logMessage.getBytes(), StandardOpenOption.CREATE,
                    StandardOpenOption.APPEND);

            // Send back a response
            response.setContentType("text/plain");
            response.getWriter().write("Term Uploaded Successfully");
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("text/plain");
            response.getWriter().write("error: " + e.getMessage());
        }

    }
}
