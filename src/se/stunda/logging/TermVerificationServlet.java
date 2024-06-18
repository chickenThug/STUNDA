package se.stunda.logging;

import java.io.*;
import java.nio.file.*;
import javax.servlet.*;
import javax.servlet.http.*;
import com.opencsv.*;

public class TermVerificationServlet extends HttpServlet {
    private static final String TERM_FILE_PATH = "/var/lib/stunda/terms/unprocessed.csv";

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("text/csv");
        response.setCharacterEncoding("UTF-8");

        try (Reader reader = Files.newBufferedReader(Paths.get(TERM_FILE_PATH))) {
            // Directly copy CSV content to response
            Files.copy(Paths.get(TERM_FILE_PATH), response.getOutputStream());
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("text/plain");
            response.getWriter().write("error:" + e.getMessage());
        }
    }
}
