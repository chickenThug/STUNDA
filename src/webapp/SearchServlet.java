import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;

public class SearchServlet extends HttpServlet {
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String query = request.getParameter("query");
        // Perform search based on the query
        // For demonstration, let's just echo back the search query
        response.setContentType("text/html");
        PrintWriter out = response.getWriter();
        out.println("<html><head><title>Search Result</title></head><body>");
        out.println("<h1>Search Result</h1>");
        out.println("<p>You searched for: " + query + "</p>");
        out.println("</body></html>");
    }
}