package se.stunda.logging;

import org.json.JSONArray;
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

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        try {
            StringBuilder jsonBuffer = new StringBuilder();
            String line;
            while ((line = request.getReader().readLine()) != null) {
                jsonBuffer.append(line);
            }
            JSONArray jsonArray = new JSONArray(jsonBuffer.toString());

            // Process your JSON array here

            response.setContentType("application/json");
            response.setCharacterEncoding("UTF-8");
            response.getWriter().write(jsonArray.toString());
        } catch (JSONException e) {
            // Handle JSON parsing errors or other JSON related issues
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            response.getWriter().write("Invalid JSON data provided");
        } catch (Exception e) {
            // Handle general errors
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.getWriter().write("Internal server error occurred");
        }
    }
}
