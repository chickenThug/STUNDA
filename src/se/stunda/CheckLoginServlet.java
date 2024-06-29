package se.stunda;

import io.github.cdimascio.dotenv.Dotenv;
import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;

public class CheckLoginServlet extends HttpServlet {
    private String storedUsername;
    private String storedPassword;
    String filePath = "/var/lib/stunda/data/users.txt";

    @Override
    public void init() throws ServletException {
        super.init();
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        
        boolean found = false;
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
           
            String username = request.getParameter("username");
            String password = request.getParameter("password");
            while ((line = br.readLine()) != null) {
                // Split the line into username and password
                String[] parts = line.split("\\s+");
                if (parts.length == 2) {
                    String usernameFromFile = parts[0];
                    String passwordFromFile = parts[1];

                    // Compare username and password
                    if (usernameFromFile.equals(username) && passwordFromFile.equals(password)) {
                        found = true;
                        break;
                    }
                }
            }
        } catch (IOException e) {
            response.setContentType("application/json");
            response.getWriter().write("{\"valid\":" + false + "}");
        } 

        response.setContentType("application/json");
        response.getWriter().write("{\"valid\":" + found + "}");
    }
}
