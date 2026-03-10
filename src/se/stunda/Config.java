package se.stunda;

public class Config {
    public static String DATA_DIR;
    public static String LOG_DIR;

    public static boolean KARP_WRITES_ENABLED;

    public static void init(String instance) {
        DATA_DIR = "/var/lib/" + instance;
        LOG_DIR  = "/var/log/" + instance;
        KARP_WRITES_ENABLED = instance.equals("stunda");
    }
}
