package se.stunda;

import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;

public class CheckLoginServlet extends HttpServlet {
    // File contianing user names and passwords
    String filePath = "/var/lib/stunda/data/users.txt";

    @Override
    public void init() throws ServletException {
        super.init();
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        
        // Boolean indicating if the provided username and password are valid
        boolean isValid = false;

        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
           
            //Provided username and password
            String username = request.getParameter("username");
            String password = request.getParameter("password");
            while ((line = br.readLine()) != null) {
                // Split the line into username and password
                String[] parts = line.split("\\s+");
                if (parts.length == 2) { 
                    // File username and password
                    String usernameFromFile = parts[0];
                    String passwordFromFile = parts[1];

                    // Compare username and password
                    if (usernameFromFile.equals(username) && passwordFromFile.equals(password)) {
                        isValid = true;
                        break;
                    }
                }
            }
        } catch (IOException e) {
            response.setContentType("application/json");
            response.getWriter().write("{\"valid\":" + false + "}");
        } 

        // Respond to server
        response.setContentType("application/json");
        response.getWriter().write("{\"valid\":" + isValid + "}");
    }
}
