package se.stunda.logging;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;
import com.opencsv.*;
import com.google.gson.*;

public class TermVerificationServlet extends HttpServlet {
    private static final String TERM_FILE_PATH = "/var/lib/stunda/terms/unprocessed.csv"; // CHANGE THIS

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");

        try (Reader reader = Files.newBufferedReader(Paths.get(TERM_FILE_PATH))) {
            CSVReader csvReader = new CSVReader(reader);
            List<String[]> records = csvReader.readAll();
            List<Map<String, String>> termsList = new ArrayList<>();

            String[] headers = records.get(0);
            for (int i = 1; i < records.size(); i++) {
                String[] record = records.get(i);
                Map<String, String> termData = new HashMap<>();
                for (int j = 0; j < headers.length; j++) {
                    termData.put(headers[j], record[j]);
                }
                termsList.add(termData);
            }

            Gson gson = new Gson();
            String json = gson.toJson(termsList);
            response.getWriter().write(json);
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("text/plain");
            response.getWriter().write("error:" + e.getMessage());
        }
    }
}