package se.stunda;

import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;

public class ConfigListener implements ServletContextListener {
    public void contextInitialized(ServletContextEvent sce) {
        String contextPath = sce.getServletContext().getContextPath();
        Config.init(contextPath.replaceFirst("^/", ""));
    }

    public void contextDestroyed(ServletContextEvent sce) {}
}
