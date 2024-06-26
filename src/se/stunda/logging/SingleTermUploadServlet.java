package se.stunda.logging;

import javax.servlet.annotation.MultipartConfig;
import javax.servlet.annotation.WebServlet;
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.nio.file.*;


@MultipartConfig
public class SingleTermUploadServlet extends HttpServlet {
    private static final String FILE_PATH = "/var/lib/stunda/terms_test/unprocessed.csv";
    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        try {
            request.setCharacterEncoding("UTF-8");
            String swedishTerm = request.getParameter("sweTerm");
            String englishTerm = request.getParameter("engTerm");
            String source =      request.getParameter("source");
            

            String logMessage = String.format("%s,%s,%s\n",
                    swedishTerm,
                    englishTerm,
                    source);

            // Using Java NIO to append text to a file in a thread-safe manner
            Files.write(Paths.get(FILE_PATH), logMessage.getBytes(), StandardOpenOption.CREATE, StandardOpenOption.APPEND);

            // Send back a response
            response.setContentType("text/plain");
            response.getWriter().write("Term Uploaded Successfully");
        }
        catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("text/plain");
            response.getWriter().write("error: " + e.getMessage());
        }
        
    }
}
