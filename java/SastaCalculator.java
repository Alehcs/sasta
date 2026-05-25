import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class SastaCalculator {
    private static final Path RUTA_CSV = Path.of("data", "aeronaves_demo.csv");
    private static final Path RUTA_SALIDA = Path.of("data", "resultados_java.csv");

    public static void main(String[] args) throws IOException {
        List<Aeronave> aeronaves = cargarAeronaves(RUTA_CSV);
        List<ResultadoCalculo> resultados = calcularProyecciones(aeronaves);
        exportarResultados(resultados, RUTA_SALIDA);
        System.out.println("Resultados Java exportados en: " + RUTA_SALIDA);
    }

    private static List<Aeronave> cargarAeronaves(Path rutaCsv) throws IOException {
        List<Aeronave> aeronaves = new ArrayList<>();

        try (BufferedReader lector = Files.newBufferedReader(rutaCsv)) {
            lector.readLine();
            String linea;

            while ((linea = lector.readLine()) != null) {
                String[] campos = linea.split(",", -1);
                if (campos.length != 7) {
                    continue;
                }

                try {
                    Aeronave aeronave = new Aeronave(
                        campos[0].trim(),
                        Double.parseDouble(campos[1].trim()),
                        Double.parseDouble(campos[2].trim()),
                        Integer.parseInt(campos[3].trim()),
                        Double.parseDouble(campos[4].trim()),
                        Double.parseDouble(campos[5].trim()),
                        Double.parseDouble(campos[6].trim())
                    );

                    if (aeronave.altZ < 0) {
                        continue;
                    }

                    if (aeronave.altZ < 100) {
                        continue;
                    }
                    aeronaves.add(aeronave);
                } catch (NumberFormatException error) {
                    // Filas corruptas se ignoran para mantener la ejecucion completa.
                }
            }
        }

        return aeronaves;
    }

    private static List<ResultadoCalculo> calcularProyecciones(List<Aeronave> aeronaves) {
        List<ResultadoCalculo> resultados = new ArrayList<>();

        for (int i = 0; i < aeronaves.size(); i++) {
            for (int j = i + 1; j < aeronaves.size(); j++) {
                Aeronave aeronaveA = aeronaves.get(i);
                Aeronave aeronaveB = aeronaves.get(j);

                double[] velocidadA = descomponerVelocidad(aeronaveA);
                double[] velocidadB = descomponerVelocidad(aeronaveB);

                double vx1 = velocidadA[0];
                double vy1 = velocidadA[1];
                double vx2 = velocidadB[0];
                double vy2 = velocidadB[1];

                double dx = aeronaveB.posX - aeronaveA.posX;
                double dy = aeronaveB.posY - aeronaveA.posY;
                double dvx = vx2 - vx1;
                double dvy = vy2 - vy1;

                double velocidadRelativaCuadrada = (dvx * dvx) + (dvy * dvy);
                double tiempoCritico;
                if (velocidadRelativaCuadrada == 0) {
                    tiempoCritico = 0;
                } else {
                    tiempoCritico = -((dx * dvx) + (dy * dvy)) / velocidadRelativaCuadrada;
                }

                double x1Futuro = aeronaveA.posX + vx1 * tiempoCritico;
                double y1Futuro = aeronaveA.posY + vy1 * tiempoCritico;
                double x2Futuro = aeronaveB.posX + vx2 * tiempoCritico;
                double y2Futuro = aeronaveB.posY + vy2 * tiempoCritico;

                double distanciaHorizontalNm = Math.sqrt(
                    Math.pow(x2Futuro - x1Futuro, 2) + Math.pow(y2Futuro - y1Futuro, 2)
                );

                double alt1Futura = aeronaveA.altZ + aeronaveA.tasaV * tiempoCritico;
                double alt2Futura = aeronaveB.altZ + aeronaveB.tasaV * tiempoCritico;
                double distanciaVerticalFt = Math.abs(alt2Futura - alt1Futura);

                resultados.add(
                    new ResultadoCalculo(
                        aeronaveA.id,
                        aeronaveB.id,
                        tiempoCritico,
                        distanciaHorizontalNm,
                        distanciaVerticalFt
                    )
                );
            }
        }

        return resultados;
    }

    private static double[] descomponerVelocidad(Aeronave aeronave) {
        double velHNmMin = aeronave.velH / 60;
        double anguloRad = Math.toRadians(aeronave.angulo);
        double vx = velHNmMin * Math.sin(anguloRad);
        double vy = velHNmMin * Math.cos(anguloRad);

        return new double[] {vx, vy};
    }

    private static void exportarResultados(List<ResultadoCalculo> resultados, Path rutaSalida) throws IOException {
        try (BufferedWriter escritor = Files.newBufferedWriter(rutaSalida)) {
            escritor.write("id_a,id_b,tiempo_min,distancia_horizontal_nm,distancia_vertical_ft");
            escritor.newLine();

            for (ResultadoCalculo resultado : resultados) {
                escritor.write(
                    String.format(
                        Locale.US,
                        "%s,%s,%.12f,%.12f,%.12f",
                        resultado.idA,
                        resultado.idB,
                        resultado.tiempoMin,
                        resultado.distanciaHorizontalNm,
                        resultado.distanciaVerticalFt
                    )
                );
                escritor.newLine();
            }
        }
    }

    private static class Aeronave {
        String id;
        double posX;
        double posY;
        int altZ;
        double velH;
        double angulo;
        double tasaV;

        Aeronave(String id, double posX, double posY, int altZ, double velH, double angulo, double tasaV) {
            this.id = id;
            this.posX = posX;
            this.posY = posY;
            this.altZ = altZ;
            this.velH = velH;
            this.angulo = angulo;
            this.tasaV = tasaV;
        }
    }

    private static class ResultadoCalculo {
        String idA;
        String idB;
        double tiempoMin;
        double distanciaHorizontalNm;
        double distanciaVerticalFt;

        ResultadoCalculo(
            String idA,
            String idB,
            double tiempoMin,
            double distanciaHorizontalNm,
            double distanciaVerticalFt
        ) {
            this.idA = idA;
            this.idB = idB;
            this.tiempoMin = tiempoMin;
            this.distanciaHorizontalNm = distanciaHorizontalNm;
            this.distanciaVerticalFt = distanciaVerticalFt;
        }
    }
}
