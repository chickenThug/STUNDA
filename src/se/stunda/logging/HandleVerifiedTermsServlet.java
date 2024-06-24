package se.stunda.logging;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.github.cdimascio.dotenv.Dotenv;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;

public class HandleVerifiedTermsServlet extends HttpServlet {
    private static final String UNAPPROVED_FILE_PATH = "/var/lib/stunda/terms/unapproved.csv";
    private static final String APPROVED_FILE_PATH = "/var/lib/stunda/terms/approved.csv";
    private static final Dotenv dotenv = Dotenv.load();

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        try {
            response.setContentType("application/json;charset=UTF-8");

            // Ensure directories exist
            createDirectoriesIfNeeded(UNAPPROVED_FILE_PATH);
            createDirectoriesIfNeeded(APPROVED_FILE_PATH);

            ObjectMapper mapper = new ObjectMapper();
            Map<String, List<Map<String, String>>> termsData = mapper.readValue(request.getInputStream(), Map.class);

            List<Map<String, String>> approvedTerms = termsData.get("approvedTerms");
            List<Map<String, String>> notApprovedTerms = termsData.get("notApprovedTerms");

            // Load API key
            String apiKey = dotenv.get("KARP_API_KEY");

            // Add approved terms to the database
            for (Map<String, String> term : approvedTerms) {
                String newID = addEntry(apiKey, term);
                if (newID != null) {
                    System.out.println("Term added with new ID: " + newID);
                } else {
                    System.err.println("Failed to add term: " + term);
                }
            }

            // Write approved terms to approved CSV file
            writeTermsToCSV(APPROVED_FILE_PATH, approvedTerms);

            // Write not approved terms to unapproved CSV file
            writeTermsToCSV(UNAPPROVED_FILE_PATH, notApprovedTerms);

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

    private String addEntry(String apiKey, Map<String, String> entry) {
        String url = "https://spraakbanken4.it.gu.se/karp/v7/entries/stunda";
        String responseNewID = null;

        try {
            URL urlObj = new URL(url + "?api_key=" + URLEncoder.encode(apiKey, StandardCharsets.UTF_8.toString()));
            HttpURLConnection connection = (HttpURLConnection) urlObj.openConnection();
            connection.setRequestMethod("PUT");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);

            // Prepare JSON payload
            Map<String, Object> data = Map.of(
                    "entry", entry,
                    "message", "");
            ObjectMapper objectMapper = new ObjectMapper();
            String jsonPayload = objectMapper.writeValueAsString(data);

            // Send JSON payload
            try (OutputStream os = connection.getOutputStream()) {
                byte[] input = jsonPayload.getBytes(StandardCharsets.UTF_8);
                os.write(input, 0, input.length);
            }

            // Read response
            int responseCode = connection.getResponseCode();
            if (responseCode == HttpURLConnection.HTTP_CREATED) {
                try (BufferedReader in = new BufferedReader(
                        new InputStreamReader(connection.getInputStream(), StandardCharsets.UTF_8))) {
                    StringBuilder response = new StringBuilder();
                    String inputLine;
                    while ((inputLine = in.readLine()) != null) {
                        response.append(inputLine);
                    }
                    // Parse response JSON to get newID
                    Map<String, Object> responseJson = objectMapper.readValue(response.toString(), Map.class);
                    responseNewID = (String) responseJson.get("newID");
                }
            } else {
                System.err.println("Unsuccessful add: " + responseCode);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        return responseNewID;
    }

    private void writeTermsToCSV(String filePath, List<Map<String, String>> terms) throws IOException {
        try (FileWriter fileWriter = new FileWriter(filePath, true);
                PrintWriter printWriter = new PrintWriter(fileWriter)) {

            for (Map<String, String> term : terms) {
                printWriter.println(convertTermToCSV(term));
            }

        } catch (IOException e) {
            throw new IOException("Failed to write to CSV file", e);
        }
    }

    private String convertTermToCSV(Map<String, String> term) {
        StringBuilder csvBuilder = new StringBuilder();
        term.forEach((key, value) -> csvBuilder.append(value).append(","));
        // Remove trailing comma
        if (csvBuilder.length() > 0) {
            csvBuilder.setLength(csvBuilder.length() - 1);
        }
        return csvBuilder.toString();
    }
}
