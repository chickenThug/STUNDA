package se.stunda;

import javax.servlet.annotation.MultipartConfig;
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.nio.file.*;

@MultipartConfig
public class SingleTermUploadServlet extends HttpServlet {
    private static final String FILE_PATH = Config.DATA_DIR + "/terms/unprocessed.csv";

    private static String csvQuote(String field) {
        if (field != null && field.contains(",") && !field.startsWith("\"")) {
            return "\"" + field + "\"";
        }
        return field;
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        try {
            request.setCharacterEncoding("UTF-8");
            
            // get parameters
            String swedishTerm = request.getParameter("sweTerm");
            String englishTerm = request.getParameter("engTerm");
            String source = request.getParameter("source");

            // Format entry for storage, quoting fields that contain commas
            String entry = String.format("%s,%s,%s\n",
                    csvQuote(englishTerm),
                    csvQuote(swedishTerm),
                    csvQuote(source));

            // Add entry to file containing unprocessed terms
            Files.write(Paths.get(FILE_PATH), entry.getBytes("utf-8"), StandardOpenOption.CREATE,
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
