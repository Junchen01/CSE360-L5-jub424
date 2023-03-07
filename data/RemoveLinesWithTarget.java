import java.io.*;

public class RemoveLinesWithTarget {
    public static void main(String[] args) {
        String inputFile = "TrajectoryTrackingRectangular_2.txt";
        String outputFile = "output.txt";
        String target = "target";

        try (BufferedReader br = new BufferedReader(new FileReader(inputFile));
             BufferedWriter bw = new BufferedWriter(new FileWriter(outputFile))) {

            String line;
            while ((line = br.readLine()) != null) {
                if (!line.startsWith(target)) {
                    bw.write(line);
                    bw.newLine();
                }
            }

        } catch (IOException e) {
            e.printStackTrace();
        }

        // Delete the original file
        File originalFile = new File(inputFile);
        originalFile.delete();

        // Rename the new file to the original filename
        File newFile = new File(outputFile);
        newFile.renameTo(originalFile);
    }
}
