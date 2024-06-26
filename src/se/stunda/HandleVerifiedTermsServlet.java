package se.stunda;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;
import javax.servlet.*;
import javax.servlet.http.*;

import java.io.*;
import java.util.HashSet;
import java.util.Set;
import io.github.cdimascio.dotenv.Dotenv;

import java.net.URL;
import java.net.URLEncoder;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.net.HttpURLConnection;

public class HandleVerifiedTermsServlet extends HttpServlet {
    private static final String UNAPPROVED_FILE_PATH = "/var/lib/stunda/terms/notapproved.jsonl";
    private static final String APPROVED_FILE_PATH = "/var/lib/stunda/terms/approved.jsonl";
    private static final String PROCESSED_FILE_PATH = "/var/lib/stunda/terms/processed.jsonl";
    private static final String LOG_FILE_PATH = "/var/log/stunda/log_verify.txt";

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        try {
            // Load environment file
            Dotenv dotenv = Dotenv.configure()
                    .directory("/var/lib/stunda/data")
                    .ignoreIfMalformed()
                    .ignoreIfMissing()
                    .load();

            String api_key = dotenv.get("KARP_API_KEY");

            StringBuilder jsonBuffer = new StringBuilder();
            String line;
            request.setCharacterEncoding("UTF-8");

            // Read request line by line
            while ((line = request.getReader().readLine()) != null) {
                jsonBuffer.append(line);
            }

            JSONObject incomingData = new JSONObject(jsonBuffer.toString());

            // Load username of the user approving the term
            String username = incomingData.getString("username");
            JSONArray incomingTerms = incomingData.getJSONArray("terms");

            JSONArray approvedArray = new JSONArray();
            JSONArray notApprovedArray = new JSONArray();

            // Set to store the incoming terms so they can be removed from processed.jsonl
            Set<String> incomingTermIds = new HashSet<>();

            DateTimeFormatter dtf = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
            LocalDateTime now = LocalDateTime.now();

            for (int i = 0; i < incomingTerms.length(); i++) {
                JSONObject jsonObject = incomingTerms.getJSONObject(i);

                // Determine whether the jsonObject is approved
                boolean isApproved = jsonObject.optBoolean("approved", false);
                
                // Add the incoming term to the set of seen terms
                incomingTermIds.add(jsonObject.getString("eng_lemma") + jsonObject.getString("swe_lemma")
                        + jsonObject.getString("src"));

                // Remove the 'approved' key from the JSONObject
                jsonObject.remove("approved");

                // Split the incoming terms into approved and not approved
                if (isApproved) {
                    approvedArray.put(jsonObject);
                } else {
                    notApprovedArray.put(jsonObject);
                }

                // Format logmessage
                String logMessage = String.format(
                        "Username: %s, Swe Lemma: %s, Eng Lemma: %s, Timestamp: %s, Approved: %s\n",
                        username, jsonObject.getString("swe_lemma"), jsonObject.getString("eng_lemma"), dtf.format(now),
                        isApproved ? "approved" : "not approved");
                
                // Append log message to log
                Files.write(Paths.get(LOG_FILE_PATH), logMessage.getBytes(), StandardOpenOption.CREATE,
                        StandardOpenOption.APPEND);
            }

            // Array to store terms not verified by user
            JSONArray remainingProcessedTerms = new JSONArray();

            try (BufferedReader reader = new BufferedReader(new FileReader(PROCESSED_FILE_PATH))) {
                while ((line = reader.readLine()) != null) {
                    JSONObject jsonObject = new JSONObject(line);
                    // Check if term has been manually verified
                    if (!incomingTermIds.contains(jsonObject.getString("eng_lemma") + jsonObject.getString("swe_lemma")
                            + jsonObject.getString("src"))) {
                        remainingProcessedTerms.put(jsonObject);
                    }

                }
            }

            // Write not approved terms to file
            writeToJsonlFile(notApprovedArray, UNAPPROVED_FILE_PATH, true);

            Set<String> allowedPos = new HashSet<>();
            allowedPos.add("N");
            allowedPos.add("V");
            allowedPos.add("NP");
            allowedPos.add("A");
            allowedPos.add("Ab");

            for (int i = 0; i < approvedArray.length(); i++) {
                JSONObject obj = approvedArray.getJSONObject(i);
                // Process each JSONObject
                String engLemma = obj.getString("eng_lemma");
                String sweLemma = obj.getString("swe_lemma");
                String src = obj.getString("src");
                JSONArray engInflections = obj.optJSONArray("english_inflections");
                JSONArray sweInflections = obj.optJSONArray("swedish_inflections");
                String pos = obj.getString("agreed_pos");

                // Array of sources
                String[] incoming_srcs = src.split(", ");
                
                // Search if terms exists on KARP
                JSONObject karpSearch = getTerm(engLemma, sweLemma);

                JSONArray hits = karpSearch.optJSONArray("hits");

                boolean already_exist = false;

                // Iterate through hits
                for (int j = 0; j < hits.length(); j++) {
                    JSONObject hit = hits.getJSONObject(j);
                    String id = hit.getString("id");
                    int version = hit.getInt("version");
                    JSONObject entry = hit.optJSONObject("entry");

                    String new_source;

                    // Term already exists
                    if ((entry.optJSONObject("eng").getString("lemma").equals(engLemma))
                            && (entry.optJSONObject("swe").getString("lemma").equals(sweLemma))) {
                        already_exist = true;

                        // Check if the source also already exists
                        new_source = entry.getString("src");
                        String[] current_srcs = new_source.split(", ");
                        for (String inc_src : incoming_srcs) {
                            for (String cur_srcs : current_srcs) {
                                if (!inc_src.equals(cur_srcs)) {
                                    new_source += ", " + inc_src;
                                }
                            }
                        }
                        entry.put("src", new_source);
                        updateTerm(id, entry, version, api_key, false);
                        break;
                    }
                }
                if (already_exist) {
                    continue;
                } else { // New entry 
                    JSONObject eng = new JSONObject();
                    JSONObject swe = new JSONObject();

                    eng.put("lemma", engLemma);
                    swe.put("lemma", sweLemma);

                    if (engInflections == null) {
                        eng.put("inflections", new JSONArray());
                    } else {
                        eng.put("inflections", engInflections);
                    }

                    // Check and assign "inflections" for "swe"
                    if (sweInflections == null) {
                        swe.put("inflections", new JSONArray());
                    } else {
                        swe.put("inflections", sweInflections);
                    }

                    JSONObject new_entry = new JSONObject();

                    new_entry.put("src", src);
                    new_entry.put("eng", eng);
                    new_entry.put("swe", swe);

                    if (allowedPos.contains(pos)) {
                        new_entry.put("pos", pos);
                    }

                    addEntry(api_key, new_entry, false);
                }
            }

            // Write the remaining terms to be processed to file
            writeToJsonlFile(remainingProcessedTerms, PROCESSED_FILE_PATH, false);

            // Write approved terms to file
            writeToJsonlFile(approvedArray, APPROVED_FILE_PATH, true);

            response.setContentType("text/plain");
            response.getWriter().write("success");
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
            response.getWriter().write("Internal server error occurred: " + e.getMessage());
        }
    }

    // Helper function for writing to list of JSON objects to file
    private static void writeToJsonlFile(JSONArray jsonArray, String filePath, boolean append) {
        try (FileWriter fileWriter = new FileWriter(filePath, append)) {
            for (int i = 0; i < jsonArray.length(); i++) {
                fileWriter.write(jsonArray.getJSONObject(i).toString() + "\n");
            }
        } catch (IOException e) {
            System.err.println("Error writing to file: " + e.getMessage());
        }
    }

    // Helper function for searching against KARP
    public static JSONObject getTerm(String eng_lemma, String swe_lemma) {
        JSONObject jsonResponse = new JSONObject();

        try {
            String urlString = "https://spraakbanken4.it.gu.se/karp/v7/query/stunda?q=and(equals|eng.lemma|"
                    + URLEncoder.encode(eng_lemma, "UTF-8") + "||equals|swe.lemma|"
                    + URLEncoder.encode(swe_lemma, "UTF-8") + ")&from=0&size=100";
            URL url = new URL(urlString);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");

            int responseCode = conn.getResponseCode();

            if (responseCode == 200) { // success
                BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                String inputLine;
                StringBuffer response = new StringBuffer();

                while ((inputLine = in.readLine()) != null) {
                    response.append(inputLine);
                }
                in.close();

                jsonResponse = new JSONObject(response.toString());
                System.out.println("Successful GET");
            } else {
                System.out.println("Error: " + responseCode);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        return jsonResponse;
    }

    // Helper function for updating an entry on KARP
    public static JSONObject updateTerm(String id, JSONObject entry, int version, String apiKey, boolean verbose) {
        String urlString = "https://spraakbanken4.it.gu.se/karp/v7/entries/stunda/" + id;
        JSONObject jsonResponse = null;

        try {
            URL url = new URL(urlString + "?api_key=" + apiKey);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setRequestProperty("Accept", "*/*");
            conn.setRequestProperty("Connection", "keep-alive");
            conn.setDoOutput(true);

            JSONObject data = new JSONObject();
            data.put("entry", entry);
            data.put("message", "");
            data.put("version", version);

            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = data.toString().getBytes("utf-8");
                os.write(input, 0, input.length);
            }

            int responseCode = conn.getResponseCode();
            BufferedReader in;
            if (responseCode == 200) {
                in = new BufferedReader(new InputStreamReader(conn.getInputStream(), "utf-8"));
                StringBuilder response = new StringBuilder();
                String responseLine;
                while ((responseLine = in.readLine()) != null) {
                    response.append(responseLine.trim());
                }
                jsonResponse = new JSONObject(response.toString());
                if (verbose) {
                    System.out.println("Successful update");
                }
            } else {
                in = new BufferedReader(new InputStreamReader(conn.getErrorStream(), "utf-8"));
                StringBuilder response = new StringBuilder();
                String responseLine;
                while ((responseLine = in.readLine()) != null) {
                    response.append(responseLine.trim());
                }
                if (verbose) {
                    System.out.println("Unsuccessful update: " + responseCode + ", " + response.toString());
                }
            }
            in.close();

        } catch (Exception e) {
            e.printStackTrace();
        }

        return jsonResponse;
    }

    // Helper function for adding an entry to KARP
    public static String addEntry(String apiKey, JSONObject entry, boolean verbose) {
        String urlString = "https://spraakbanken4.it.gu.se/karp/v7/entries/stunda";
        String newID = null;

        try {
            URL url = new URL(urlString + "?api_key=" + apiKey);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("PUT");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setDoOutput(true);

            JSONObject data = new JSONObject();
            data.put("entry", entry);
            data.put("message", "");

            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = data.toString().getBytes("utf-8");
                os.write(input, 0, input.length);
            }

            int responseCode = conn.getResponseCode();
            BufferedReader in;
            if (responseCode == 201) {
                in = new BufferedReader(new InputStreamReader(conn.getInputStream(), "utf-8"));
                StringBuilder response = new StringBuilder();
                String responseLine;
                while ((responseLine = in.readLine()) != null) {
                    response.append(responseLine.trim());
                }
                JSONObject jsonResponse = new JSONObject(response.toString());
                newID = jsonResponse.getString("newID");
                if (verbose) {
                    System.out.println("Successful add");
                }
            } else {
                in = new BufferedReader(new InputStreamReader(conn.getErrorStream(), "utf-8"));
                StringBuilder response = new StringBuilder();
                String responseLine;
                while ((responseLine = in.readLine()) != null) {
                    response.append(responseLine.trim());
                }
                if (verbose) {
                    System.out.println("Unsuccessful add: " + responseCode + ", " + response.toString());
                }
            }
            in.close();

        } catch (Exception e) {
            e.printStackTrace();
        }

        return newID;
    }
}
