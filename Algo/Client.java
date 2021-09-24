import java.io.*;
import java.net.*;


public class Client {
    public static void main(String args[]) throws Exception{

            Socket socket = new Socket("192.168.10.1", 5000);
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true)
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        try{
            String str = "", str2 = "";
            while(!str.equals("stop")){
                str = br.readLine();
                out.print(str)

                str2 = in.readLine()
                // must put the \n for it to work properly
                System.out.println("Server Replied:" + str2 + "\n");
            }
        }
        catch(Exception e){
            System.out.println(e);
        }
        finally{
            out.close();
            socket.close();
        }
    }
}