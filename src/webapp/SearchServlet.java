import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet("/search")
public class SearchServlet extends HttpServlet {
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        // Get the search query from the request
        String query = request.getParameter("query");
        
        // Perform search processing here (not implemented in this example)
        
        // For demonstration purposes, let's just forward to a search results page
        request.setAttribute("query", query);
        request.getRequestDispatcher("/searchResults.jsp").forward(request, response);
    }
}