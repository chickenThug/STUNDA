package se.stunda.logging;

import io.github.cdimascio.dotenv.Dotenv;
import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;

public class CheckLoginServlet extends HttpServlet {
    private String storedUsername;
    private String storedPassword;

    @Override
    public void init() throws ServletException {
        super.init();
        Dotenv dotenv = Dotenv.configure()
                .directory("/var/lib/stunda/data")
                .ignoreIfMalformed()
                .ignoreIfMissing()
                .load();

        storedUsername = dotenv.get("USERNAME_VERIFY");
        storedPassword = dotenv.get("PASSWORD_VERIFY");
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        String username = request.getParameter("username");
        String password = request.getParameter("password");

        boolean isValid = storedUsername.equals(username) && storedPassword.equals(password);

        response.setContentType("application/json");
        response.getWriter().write("{\"valid\":" + isValid + "}");
    }
}
