package se.stunda.logging;

import com.fasterxml.jackson.databind.ObjectMapper;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

public class HandleVerifiedTermsServlet extends HttpServlet {
    private static final String UNAPPROVED_FILE_PATH = "/var/lib/stunda/terms/unapproved.jsonl";
    private static final String APPROVED_FILE_PATH = "/var/lib/stunda/terms/approved.jsonl";
    private static final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        try {
            response.setContentType("application/json;charset=UTF-8");

            // Ensure directories exist
            createDirectoriesIfNeeded(UNAPPROVED_FILE_PATH);
            createDirectoriesIfNeeded(APPROVED_FILE_PATH);

            // Read JSON data from request body
            BufferedReader reader = request.getReader();
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
            }

            // Convert JSON string to Java objects
            VerificationData verificationData = objectMapper.readValue(sb.toString(), VerificationData.class);

            // Write approved terms to approved JSONL file
            writeTermsToJsonl(APPROVED_FILE_PATH, verificationData.approvedTerms);

            // Write not approved terms to unapproved JSONL file
            writeTermsToJsonl(UNAPPROVED_FILE_PATH, verificationData.notApprovedTerms);

            response.setStatus(HttpServletResponse.SC_OK);
            response.getWriter().write("{\"status\":\"success\"}");
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("text/plain");
            response.getWriter().write("error: " + e.getMessage());
        }
    }

    private void createDirectoriesIfNeeded(String filePath) throws IOException {
        Path path = Paths.get(filePath);
        Path parentDir = path.getParent();
        if (!Files.exists(parentDir)) {
            Files.createDirectories(parentDir);
        }
    }

    private void writeTermsToJsonl(String filePath, List<Term> terms) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(filePath, true))) {
            for (Term term : terms) {
                writer.println(objectMapper.writeValueAsString(term));
            }
        }
    }

    // Define data classes to match the JSON structure
    private static class VerificationData {
        List<Term> approvedTerms;
        List<Term> notApprovedTerms;
    }

    private static class Term {
        String eng_term;
        String swe_term;
        String src;
    }
}
