package se.stunda.logging;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.Part;

public class TermUploadServlet extends HttpServlet {

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("text/html;charset=UTF-8");

        // Check if we have a file upload request
        if (request.getContentType() != null && request.getContentType().toLowerCase().contains("multipart/form-data")) {
            // Get the part of the request that contains the file
            Part filePart = request.getPart("csvfile");

            if (filePart != null) {
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(filePart.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        response.getWriter().println(line + "<br>");
                    }
                }
            } else {
                response.getWriter().println("No file uploaded!");
            }
        } else {
            response.getWriter().println("Invalid request content type!");
        }
    }
}