package se.stunda.logging;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.IOException;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

public class HandleVerifiedTermsServlet extends HttpServlet {
    private static final String UNAPPROVED_FILE_PATH = "/var/lib/stunda/terms_test/notapproved.jsonl";
    private static final String APPROVED_FILE_PATH = "/var/lib/stunda/terms_test/approved.jsonl";
    private static final String PROCESSED_FILE_PATH = "/var/lib/stunda/terms_test/processed.jsonl";

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        try {
            StringBuilder jsonBuffer = new StringBuilder();
            String line;
            while ((line = request.getReader().readLine()) != null) {
                jsonBuffer.append(line);
            }
            JSONArray incomingTerms = new JSONArray(jsonBuffer.toString());
            
            JSONArray approvedArray = new JSONArray();
            JSONArray notApprovedArray = new JSONArray();

            Set<String> incomingTermIds = new HashSet<>();

            for (int i = 0; i < incomingTerms.length(); i++) {
                JSONObject jsonObject = incomingTerms.getJSONObject(i);

                // Determine whether the jsonObject is approved
                boolean isApproved = jsonObject.optBoolean("approved", false);

                incomingTermIds.add(jsonObject.getString("eng_lemma") + jsonObject.getString("swe_lemma") + jsonObject.getString("src"));

                // Remove the 'approved' key from the JSONObject
                jsonObject.remove("approved");

                // Add to the appropriate array
                if (isApproved) {
                    approvedArray.put(jsonObject);
                } else {
                    notApprovedArray.put(jsonObject);
                }
            }

            JSONArray remainingProcessedTerms = new JSONArray();

            try (BufferedReader reader = new BufferedReader(new FileReader(PROCESSED_FILE_PATH))) {
                while ((line = reader.readLine()) != null) {
                    JSONObject jsonObject = new JSONObject(line);
                    if (!incomingTermIds.contains(jsonObject.getString("eng_lemma") + jsonObject.getString("swe_lemma") + jsonObject.getString("src"))) {
                        remainingProcessedTerms.put(jsonObject);
                    }
                    
                }
            }

            writeToJsonlFile(remainingProcessedTerms, PROCESSED_FILE_PATH, false);
            writeToJsonlFile(approvedArray, APPROVED_FILE_PATH, true);
            writeToJsonlFile(notApprovedArray, UNAPPROVED_FILE_PATH, true);


            response.setContentType("application/json");
            response.setCharacterEncoding("UTF-8");
            response.getWriter().write(incomingTerms.toString());
        } catch (JSONException e) {
            // Handle JSON parsing errors or other JSON related issues
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            response.getWriter().write("Invalid JSON data provided");
        } catch (IOException e) {
        response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
        response.getWriter().write("Error processing request: " + e.getMessage());
        } catch (Exception e) {
            // Handle general errors
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.getWriter().write("Internal server error occurred");
        }        
    }

    private static void writeToJsonlFile(JSONArray jsonArray, String filePath, boolean append) {
        try (FileWriter fileWriter = new FileWriter(filePath, append)) {
            for (int i = 0; i < jsonArray.length(); i++) {
                fileWriter.write(jsonArray.getJSONObject(i).toString() + "\n");
            }
        } catch (IOException e) {
            System.err.println("Error writing to file: " + e.getMessage());
        }
    }
}
