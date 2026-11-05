using System;
using System.Diagnostics;
using System.IO;
using System.Text;

namespace CraftAnythingPTBR
{
    class Program
    {
        static int Main(string[] args)
        {
            try
            {
                string appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
                string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                string configDir = Path.Combine(appData, "craft-anything");
                string configPath = Path.Combine(configDir, "config.toml");

                EnsurePtBrConfig(configDir, configPath);

                string localExe = Path.Combine(localAppData, "Programs", "Craft Anything", "craft-anything.exe");
                string progFilesExe = @"C:\Program Files\Craft Anything\craft-anything.exe";
                string exeDir = AppDomain.CurrentDomain.BaseDirectory;
                string siblingExe = Path.Combine(exeDir, "craft-anything-ptbr-app.exe");

                string targetExe = null;
                if (File.Exists(localExe))
                {
                    targetExe = localExe;
                }
                else if (File.Exists(siblingExe))
                {
                    targetExe = siblingExe;
                }
                else if (File.Exists(progFilesExe))
                {
                    targetExe = progFilesExe;
                }

                if (targetExe == null)
                {
                    Console.Error.WriteLine("[craft-anything-ptbr] Executavel do Craft Anything nao encontrado.");
                    return 1;
                }

                StringBuilder argBuilder = new StringBuilder();
                foreach (string a in args)
                {
                    if (argBuilder.Length > 0) argBuilder.Append(" ");
                    if (a.Contains(" ") || a.Contains("\""))
                        argBuilder.Append("\"").Append(a.Replace("\"", "\\\"")).Append("\"");
                    else
                        argBuilder.Append(a);
                }

                ProcessStartInfo psi = new ProcessStartInfo
                {
                    FileName = targetExe,
                    Arguments = argBuilder.ToString(),
                    WorkingDirectory = Path.GetDirectoryName(targetExe),
                    UseShellExecute = false
                };
                psi.EnvironmentVariables["CRAFT_ANYTHING_LANG"] = "pt-BR";

                Process proc = Process.Start(psi);
                if (proc == null)
                {
                    return 1;
                }
                return 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("[craft-anything-ptbr] Erro ao iniciar: " + ex.Message);
                return 1;
            }
        }

        private static void EnsurePtBrConfig(string configDir, string configPath)
        {
            if (!Directory.Exists(configDir))
            {
                Directory.CreateDirectory(configDir);
            }

            if (!File.Exists(configPath))
            {
                File.WriteAllText(configPath, "language = \"pt-BR\"\n", new UTF8Encoding(false));
                return;
            }

            string content = File.ReadAllText(configPath, Encoding.UTF8);
            if (!content.Contains("language ="))
            {
                content = "language = \"pt-BR\"\n" + content;
                File.WriteAllText(configPath, content, new UTF8Encoding(false));
            }
        }
    }
}
