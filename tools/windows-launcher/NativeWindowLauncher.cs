using Microsoft.Web.WebView2.WinForms;
using Microsoft.Web.WebView2.Core;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace AISearchWindowsLauncher
{
    internal static class NativeWindowProgram
    {
        private const string AppTitle = "AI Search Algorithm Visualizer Fully Portable";
        private const string FixedRuntimeVersion = "148.0.3967.96";

        public static string BrowserExecutableFolder { get; private set; }

        [STAThread]
        private static void Main()
        {
            AppDomain.CurrentDomain.AssemblyResolve += ResolveEmbeddedAssembly;
            ExtractNativeLoader();

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            try
            {
                BrowserExecutableFolder = EnsureFixedRuntime();
                Application.Run(new MainForm());
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, AppTitle, MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private static Assembly ResolveEmbeddedAssembly(object sender, ResolveEventArgs args)
        {
            var name = new AssemblyName(args.Name).Name + ".dll";
            var resourceName = "deps." + name;
            using (var stream = Assembly.GetExecutingAssembly().GetManifestResourceStream(resourceName))
            {
                if (stream == null)
                {
                    return null;
                }

                using (var memory = new MemoryStream())
                {
                    stream.CopyTo(memory);
                    return Assembly.Load(memory.ToArray());
                }
            }
        }

        private static void ExtractNativeLoader()
        {
            var arch = Environment.Is64BitProcess ? "x64" : "x86";
            var tempDir = Path.Combine(Path.GetTempPath(), "AISearchVisualizerWebView2", arch);
            Directory.CreateDirectory(tempDir);

            var loaderPath = Path.Combine(tempDir, "WebView2Loader.dll");
            var resourceName = "deps." + arch + ".WebView2Loader.dll";
            using (var stream = Assembly.GetExecutingAssembly().GetManifestResourceStream(resourceName))
            {
                if (stream == null)
                {
                    throw new InvalidOperationException("The embedded WebView2 loader is missing.");
                }

                using (var file = File.Create(loaderPath))
                {
                    stream.CopyTo(file);
                }
            }

            SetDllDirectory(tempDir);
        }

        public static string EnsureFixedRuntime()
        {
            var arch = Environment.Is64BitProcess ? "x64" : "x86";
            var runtimeRoot = GetWritableRuntimeRoot(arch);
            var marker = Path.Combine(runtimeRoot, ".ready");
            var existingRuntime = FindRuntimeFolder(runtimeRoot);
            if (File.Exists(marker) && existingRuntime != null)
            {
                return existingRuntime;
            }

            var cabPath = Path.Combine(runtimeRoot, "WebView2Runtime.cab");
            var resourceName = "deps.fixedruntime." + arch + ".cab";
            using (var stream = Assembly.GetExecutingAssembly().GetManifestResourceStream(resourceName))
            {
                if (stream == null)
                {
                    throw new InvalidOperationException("The embedded WebView2 runtime is missing.");
                }

                using (var file = File.Create(cabPath))
                {
                    stream.CopyTo(file);
                }
            }

            var expand = new ProcessStartInfo
            {
                FileName = "expand.exe",
                Arguments = "\"" + cabPath + "\" -F:* \"" + runtimeRoot + "\"",
                CreateNoWindow = true,
                UseShellExecute = false,
                WindowStyle = ProcessWindowStyle.Hidden
            };

            using (var process = Process.Start(expand))
            {
                if (process == null || !process.WaitForExit(300000) || process.ExitCode != 0)
                {
                    throw new InvalidOperationException("Could not unpack the bundled WebView2 runtime.");
                }
            }

            try { File.Delete(cabPath); } catch { }

            var runtimeFolder = FindRuntimeFolder(runtimeRoot);
            if (runtimeFolder == null)
            {
                throw new InvalidOperationException("The bundled WebView2 runtime was unpacked, but msedgewebview2.exe was not found.");
            }

            GrantWebView2RuntimeAccess(runtimeFolder);
            File.WriteAllText(marker, DateTime.UtcNow.ToString("O"));
            return runtimeFolder;
        }

        private static string GetWritableRuntimeRoot(string arch)
        {
            var suffix = Path.Combine("AISearchVisualizer", "FixedWebView2", FixedRuntimeVersion, arch);
            var candidates = new[]
            {
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                Path.GetTempPath()
            };

            foreach (var candidate in candidates)
            {
                if (string.IsNullOrWhiteSpace(candidate))
                {
                    continue;
                }

                try
                {
                    var root = Path.Combine(candidate, suffix);
                    Directory.CreateDirectory(root);
                    return root;
                }
                catch { }
            }

            throw new InvalidOperationException("Could not find a writable location for the bundled WebView2 runtime.");
        }

        private static string FindRuntimeFolder(string root)
        {
            if (!Directory.Exists(root))
            {
                return null;
            }

            var runtimeExe = Directory.GetFiles(root, "msedgewebview2.exe", SearchOption.AllDirectories).FirstOrDefault();
            return runtimeExe == null ? null : Path.GetDirectoryName(runtimeExe);
        }

        private static void GrantWebView2RuntimeAccess(string runtimeFolder)
        {
            RunIcacls(runtimeFolder, "*S-1-15-2-2:(OI)(CI)(RX)");
            RunIcacls(runtimeFolder, "*S-1-15-2-1:(OI)(CI)(RX)");
        }

        private static void RunIcacls(string runtimeFolder, string grant)
        {
            try
            {
                var startInfo = new ProcessStartInfo
                {
                    FileName = "icacls.exe",
                    Arguments = "\"" + runtimeFolder + "\" /grant " + grant,
                    CreateNoWindow = true,
                    UseShellExecute = false,
                    WindowStyle = ProcessWindowStyle.Hidden
                };

                using (var process = Process.Start(startInfo))
                {
                    if (process != null)
                    {
                        process.WaitForExit(15000);
                    }
                }
            }
            catch
            {
                // WebView2 can still work on many systems without this ACL update.
            }
        }

        [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
        private static extern bool SetDllDirectory(string lpPathName);
    }

    internal sealed class MainForm : Form
    {
        private readonly EmbeddedWebServer server;
        private readonly WebView2 webView;

        public MainForm()
        {
            Text = "AI Search Algorithm Visualizer Fully Portable";
            StartPosition = FormStartPosition.CenterScreen;
            MinimumSize = new Size(1100, 720);
            Size = new Size(1400, 900);
            Icon = SystemIcons.Application;

            server = new EmbeddedWebServer(FindFreePort());
            server.Start();

            webView = new WebView2 { Dock = DockStyle.Fill };
            Controls.Add(webView);

            Load += MainFormLoad;
            FormClosed += delegate { server.Dispose(); };
        }

        private async void MainFormLoad(object sender, EventArgs e)
        {
            var userDataFolder = Path.Combine(Path.GetTempPath(), "AISearchVisualizerWebView2", "UserData");
            Directory.CreateDirectory(userDataFolder);
            var environment = await CoreWebView2Environment.CreateAsync(NativeWindowProgram.BrowserExecutableFolder, userDataFolder);
            await webView.EnsureCoreWebView2Async(environment);
            webView.CoreWebView2.Settings.AreDefaultContextMenusEnabled = true;
            webView.CoreWebView2.Settings.AreDevToolsEnabled = false;
            webView.CoreWebView2.Navigate("http://127.0.0.1:" + server.Port + "/index.html");
        }

        private static int FindFreePort()
        {
            var listener = new TcpListener(IPAddress.Loopback, 0);
            listener.Start();
            var port = ((IPEndPoint)listener.LocalEndpoint).Port;
            listener.Stop();
            return port;
        }
    }

    internal sealed class EmbeddedWebServer : IDisposable
    {
        private static readonly Dictionary<string, string> ResourceMap = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            { "/", "index.html" },
            { "/index.html", "index.html" },
            { "/styles.css", "styles.css" },
            { "/favicon.png", "favicon.png" },
            { "/gif.worker.js", "gif.worker.js" },
            { "/Node.py", "Node.py" },
            { "/PriorityQueue.py", "PriorityQueue.py" },
            { "/SearchAgent.py", "SearchAgent.py" },
            { "/main.py", "main.py" },
            { "/docs/algorithm-guide.md", "docs/algorithm-guide.md" },
            { "/docs/api-reference.md", "docs/api-reference.md" },
            { "/docs/deployment-guide.md", "docs/deployment-guide.md" },
            { "/vendor/brython.min.js", "vendor/brython.min.js" },
            { "/vendor/brython_stdlib.js", "vendor/brython_stdlib.js" },
            { "/vendor/gif.js", "vendor/gif.js" },
            { "/vendor/jspdf.umd.min.js", "vendor/jspdf.umd.min.js" },
            { "/vendor/jszip.min.js", "vendor/jszip.min.js" },
            { "/vendor/lucide.min.js", "vendor/lucide.min.js" },
        };

        private readonly TcpListener listener;
        private readonly Thread thread;
        private volatile bool running;

        public EmbeddedWebServer(int port)
        {
            Port = port;
            listener = new TcpListener(IPAddress.Loopback, port);
            thread = new Thread(ListenLoop) { IsBackground = true };
        }

        public int Port { get; private set; }

        public void Start()
        {
            running = true;
            listener.Start();
            thread.Start();
        }

        public void Dispose()
        {
            running = false;
            try { listener.Stop(); } catch { }
        }

        private void ListenLoop()
        {
            while (running)
            {
                try
                {
                    var client = listener.AcceptTcpClient();
                    ThreadPool.QueueUserWorkItem(delegate { HandleClient(client); });
                }
                catch
                {
                    if (running)
                    {
                        Thread.Sleep(100);
                    }
                }
            }
        }

        private static void HandleClient(TcpClient client)
        {
            using (client)
            using (var stream = client.GetStream())
            using (var reader = new StreamReader(stream, Encoding.ASCII, false, 8192, true))
            {
                var requestLine = reader.ReadLine();
                if (string.IsNullOrWhiteSpace(requestLine))
                {
                    return;
                }

                string line;
                while (!string.IsNullOrEmpty(line = reader.ReadLine())) { }

                var parts = requestLine.Split(' ');
                if (parts.Length < 2 || parts[0] != "GET")
                {
                    WriteResponse(stream, 405, "text/plain; charset=utf-8", Encoding.UTF8.GetBytes("Method not allowed"));
                    return;
                }

                var rawPath = parts[1].Split('?')[0];
                var path = Uri.UnescapeDataString(rawPath);
                string resourcePath;
                if (!ResourceMap.TryGetValue(path, out resourcePath))
                {
                    WriteResponse(stream, 404, "text/plain; charset=utf-8", Encoding.UTF8.GetBytes("Not found"));
                    return;
                }

                var data = LoadResource(resourcePath);
                if (data == null)
                {
                    WriteResponse(stream, 404, "text/plain; charset=utf-8", Encoding.UTF8.GetBytes("Resource not found"));
                    return;
                }

                WriteResponse(stream, 200, GetContentType(resourcePath), data);
            }
        }

        private static byte[] LoadResource(string resourcePath)
        {
            var resourceName = "app." + resourcePath.Replace('/', '.');
            using (var stream = Assembly.GetExecutingAssembly().GetManifestResourceStream(resourceName))
            {
                if (stream == null)
                {
                    return null;
                }

                using (var memory = new MemoryStream())
                {
                    stream.CopyTo(memory);
                    return memory.ToArray();
                }
            }
        }

        private static void WriteResponse(NetworkStream stream, int statusCode, string contentType, byte[] body)
        {
            var statusText = statusCode == 200 ? "OK" : statusCode == 404 ? "Not Found" : "Method Not Allowed";
            var header = "HTTP/1.1 " + statusCode + " " + statusText + "\r\n" +
                         "Content-Type: " + contentType + "\r\n" +
                         "Content-Length: " + body.Length + "\r\n" +
                         "Cache-Control: no-store\r\n" +
                         "Connection: close\r\n\r\n";
            var headerBytes = Encoding.ASCII.GetBytes(header);
            stream.Write(headerBytes, 0, headerBytes.Length);
            stream.Write(body, 0, body.Length);
        }

        private static string GetContentType(string path)
        {
            switch (Path.GetExtension(path).ToLowerInvariant())
            {
                case ".html": return "text/html; charset=utf-8";
                case ".css": return "text/css; charset=utf-8";
                case ".js": return "application/javascript; charset=utf-8";
                case ".py": return "text/plain; charset=utf-8";
                case ".md": return "text/markdown; charset=utf-8";
                case ".png": return "image/png";
                default: return "application/octet-stream";
            }
        }
    }
}
