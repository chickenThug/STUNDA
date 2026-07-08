package se.stunda;

import com.opencsv.CSVWriter;
import javax.servlet.annotation.MultipartConfig;
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;

@MultipartConfig
public class SingleTermUploadServlet extends HttpServlet {
    private static final String FILE_PATH = Config.DATA_DIR + "/terms/unprocessed.csv";

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        try {
            request.setCharacterEncoding("UTF-8");

            // get parameters
            String swedishTerm = request.getParameter("sweTerm");
            String englishTerm = request.getParameter("engTerm");
            String source = request.getParameter("source");

            try (CSVWriter csvWriter = new CSVWriter(new FileWriter(FILE_PATH, true),
                    CSVWriter.DEFAULT_SEPARATOR,
                    CSVWriter.DEFAULT_QUOTE_CHARACTER,
                    CSVWriter.DEFAULT_ESCAPE_CHARACTER,
                    CSVWriter.DEFAULT_LINE_END)) {
                csvWriter.writeNext(new String[]{englishTerm, swedishTerm, source, ""});
            }

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
