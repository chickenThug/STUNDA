package se.stunda;

import javax.servlet.annotation.MultipartConfig;
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.nio.file.*;

@MultipartConfig
public class SingleTermUploadServlet extends HttpServlet {
    private static final String FILE_PATH = "/var/lib/stunda/terms/unprocessed.csv";

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        try {
            request.setCharacterEncoding("UTF-8");
            // get parameters
            String swedishTerm = request.getParameter("sweTerm");
            String englishTerm = request.getParameter("engTerm");
            String source = request.getParameter("source");

            // Format entry for storage
            String entry = String.format("%s,%s,%s\n",
                    englishTerm,
                    swedishTerm,
                    source);

            // Add entry to file containing unprocessed terms
            Files.write(Paths.get(FILE_PATH), entry.getBytes(), StandardOpenOption.CREATE,
                    StandardOpenOption.APPEND);

            // Send back a succesfull response
            response.setContentType("text/plain");
            response.getWriter().write("Term Uploaded Successfully");
        } catch (Exception e) {
            // Send back an error response
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("text/plain");
            response.getWriter().write("error: " + e.getMessage());
        }

    }
}
