package se.stunda.logging;

import java.io.*;
import java.nio.file.*;
import javax.servlet.*;
import javax.servlet.http.*;

public class TermVerificationServlet extends HttpServlet {
    private static final String TERM_FILE_PATH = "/var/lib/stunda/terms_test/processed.jsonl";

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");

        try (InputStream in = Files.newInputStream(Paths.get(TERM_FILE_PATH))) {
            // Copy JSONL content directly to response output stream
            byte[] buffer = new byte[1024];
            int bytesRead;
            while ((bytesRead = in.read(buffer)) != -1) {
                response.getOutputStream().write(buffer, 0, bytesRead);
            }
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("text/plain");
            response.getWriter().write("error:" + e.getMessage());
        }
    }
}
