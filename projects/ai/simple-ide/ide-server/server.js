import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import { promises as fs } from "fs";
import { dirname, join, default as path } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectPath = path.join(__dirname, "projects");

console.log(`Path for projects: ${projectPath}`);

const app = express();

// Helper function to validate if a project exists and is accessible
function validateProjectExists(projectName) {
  const projectDir = join(projectPath, projectName);
  // This would check if the directory exists and is accessible
  // For now, we'll just return a boolean for demonstration
  return fs
    .access(projectDir)
    .then(() => true)
    .catch(() => false);
}

function validateFileName(fileName) {
  const fileNameRegex = /^[A-Za-z0-9_.-]+$/;

  // Check file name format
  if (!fileNameRegex.test(fileName)) {
    return {
      valid: false,
      error:
        "Invalid file name. Only alphanumeric characters, underscores, hyphens, and dots are allowed.",
    };
  }

  return {
    valid: true,
    error: null,
  };
}

// Helper function to validate file name and check if it exists
function validateFileExists(projectName, fileName) {
  // Check for path traversal attempts - ensure file path is within project directory
  const projectDir = join(projectPath, projectName);
  const filePath = join(projectDir, fileName);

  // Verify the resolved path is within the project directory
  // Example: projects/${projectName}/${fileName} -> GOOD.
  // Example: ../${projectName}/${myBadFilename} -> BAD.
  if (!filePath.startsWith(projectDir)) {
    return {
      valid: false,
      error:
        "Invalid file path. File cannot be created outside the project directory.",
    };
  }

  // Check if file already exists
  return fs
    .access(filePath)
    .then(() => ({ valid: false, error: "File already exists." }))
    .catch(() => ({ valid: true, error: null }));
}

app.use(cors());
app.use(bodyParser.json());

app.post("/api/projects", async (req, res) => {
  try {
    const { name } = req.body;

    // Function to validate project name
    function isValidProjectName(name) {
      // Only allow alphanumeric characters, underscores, and hyphens
      const projectNameRegex = /^[a-zA-Z0-9_-]+$/;
      return projectNameRegex.test(name);
    }

    // Validate project name
    if (!name) {
      return res.status(400).json({
        error: "Project name is required.",
      });
    }

    if (!isValidProjectName(name)) {
      return res.status(400).json({
        error:
          "Invalid project name. Only alphanumeric characters, underscores, and hyphens are allowed.",
      });
    }

    // Ensure projects directory exists
    try {
      await fs.access(projectPath);
    } catch {
      await fs.mkdir(projectPath, { recursive: true });
    }

    // Create project directory
    await fs.mkdir(join(projectPath, name), { recursive: true });

    return res.status(201).json({
      message: `Created project: ${name}`,
      id: name,
    });
  } catch (err) {
    console.error("Error creating project:", err);
    return res.status(500).json({
      error: "Failed to create a project.",
    });
  }
});

app.get("/api/projects/:projectName/file/:fileName", async (req, res) => {
  const { projectName, fileName } = req.params;

  if (!(await validateProjectExists(projectName))) {
    return res.status(404).json({ error: "Project does not exist." });
  }

  const validateFilenameResult = validateFileName(fileName);
  console.log(validateFilenameResult.error);
  if (!validateFilenameResult.valid) {
    return res
      .status(400)
      .json({ error: "Invalid filename or file does not exist." });
  }

  try {
    const fileContents = (
      await fs.readFile(path.join(projectPath, projectName, fileName))
    ).toString("utf-8");

    return res.status(200).json({
      data: fileContents,
    });
  } catch {
    return res.status(500).json({
      error: "Internal server error while reading file.",
    });
  }
});

app.post("/api/projects/:projectName/file", async (req, res) => {
  const { projectName } = req.params;
  const { fileName, content } = req.body;

  // first validate if the project already exists
  // check if ${projectPath}/projectName is accessible and exists in the filesystem
  //  -> return a 404 error if not accessible or does not exist
  if (!(await validateProjectExists(projectName))) {
    return res.status(404).json({
      error: "Project does not exist.",
    });
  }

  if (!(await validateFileExists(projectName, fileName))) {
    return res.status(400).json({
      error: "File already exists.",
    });
  }

  // second validate if fileName is valid.
  //  1. it has to be the correct format (no sketchy/shady naming) - [A-Za-z0-9_.-]
  //  2. the file already doesn't exist
  try {
    const fileNameValidation = await validateFileName(projectName, fileName);
    if (!fileNameValidation.valid) {
      return res.status(400).json({
        error: fileNameValidation.error,
      });
    }
  } catch (error) {
    return res.status(500).json({
      error: "Internal server error while validating file name.",
    });
  }

  // Validate that content is text only, no binary
  if (typeof content !== "string") {
    return res.status(400).json({
      error: "Content must be text only, no binary data allowed.",
    });
  }

  const fileNamePath = join(projectPath, projectName, fileName);
  await fs.writeFile(fileNamePath, content);

  return res.status(201).json({ message: `File: ${fileName} created!` });
});

app.put("/api/projects/:projectName/file/:fileName", async (req, res) => {
  const { projectName, fileName: fileNameParam } = req.params;
  const { fileName, content } = req.body;

  // Validation
  // 1. Ensure that the filename isn't bad
  const fileNameRegex = /^[A-Za-z0-9_.-]+$/;
  if (!fileNameRegex.test(fileName)) {
    return res.status(400).json({
      error:
        "Invalid file name. Only alphanumeric characters, underscores, hyphens, and dots are allowed.",
    });
  }

  // 2. Ensure that the filename exists in the project
  const projectDir = join(projectPath, projectName);
  const filePath = join(projectDir, fileName);

  // Verify the resolved path is within the project directory
  if (!filePath.startsWith(projectDir)) {
    return res.status(400).json({
      error:
        "Invalid file path. File cannot be created outside the project directory.",
    });
  }

  try {
    await fs.access(filePath);
  } catch {
    return res.status(404).json({
      error: "File does not exist in the project.",
    });
  }

  // 3. Ensure that content is text only, no binary
  if (typeof content !== "string") {
    return res.status(400).json({
      error: "Content must be text only, no binary data allowed.",
    });
  }

  // All validations passed, update the file
  try {
    await fs.writeFile(filePath, content);
    return res.status(200).json({
      message: `${fileName} has been updated.`,
    });
  } catch (error) {
    return res.status(500).json({
      error: "Failed to update file.",
    });
  }
});

// DELETE endpoint for file removal
app.delete("/api/projects/:projectName/file/:fileName", async (req, res) => {
  const { projectName, fileName } = req.params;

  // Validation
  // 1. Ensure that the filename isn't bad
  const fileNameRegex = /^[A-Za-z0-9_.-]+$/;
  if (!fileNameRegex.test(fileName)) {
    return res.status(400).json({
      error:
        "Invalid file name. Only alphanumeric characters, underscores, hyphens, and dots are allowed.",
    });
  }

  // 2. Ensure that the filename exists in the project
  const projectDir = join(projectPath, projectName);
  const filePath = join(projectDir, fileName);

  // Verify the resolved path is within the project directory
  if (!filePath.startsWith(projectDir)) {
    return res.status(400).json({
      error:
        "Invalid file path. File cannot be created outside the project directory.",
    });
  }

  try {
    await fs.access(filePath);
  } catch {
    return res.status(404).json({
      error: "File does not exist in the project.",
    });
  }

  // All validations passed, delete the file
  try {
    await fs.unlink(filePath);
    return res.status(200).json({
      message: `${fileName} has been deleted.`,
    });
  } catch (error) {
    return res.status(500).json({
      error: "Failed to delete file.",
    });
  }
});

app.get("/api/projects", async (req, res) => {
  try {
    const projectDirs = await fs.readdir(projectPath);
    const projects = projectDirs.filter(async (dir) => {
      try {
        const stats = await fs.stat(join(projectPath, dir));
        return stats.isDirectory();
      } catch {
        return false;
      }
    });

    // Filter returns a promise, so we need to resolve it
    const resolvedProjects = await Promise.all(projects);
    return res.status(200).json({
      projects: resolvedProjects,
    });
  } catch (error) {
    console.error("Error listing projects:", error);
    return res.status(500).json({
      error: "Failed to list projects.",
    });
  }
});

app.get("/api/projects/:projectName/files", async (req, res) => {
  const { projectName } = req.params;

  // Validate project exists
  if (!(await validateProjectExists(projectName))) {
    return res.status(404).json({
      error: "Project does not exist.",
    });
  }

  try {
    const projectDir = join(projectPath, projectName);
    const files = await fs.readdir(projectDir);

    // Filter out directories, only return files
    const fileDetails = [];
    for (const file of files) {
      const filePath = join(projectDir, file);
      const stats = await fs.stat(filePath);
      if (stats.isFile()) {
        fileDetails.push({
          name: file,
          size: stats.size,
          modified: stats.mtime.toISOString(),
        });
      }
    }

    return res.status(200).json({
      files: fileDetails,
    });
  } catch (error) {
    return res.status(500).json({
      error: "Failed to list files.",
    });
  }
});

// POST endpoint for compiling C files
app.post("/api/projects/:projectName/compile/:fileName", async (req, res) => {
  const { projectName, fileName } = req.params;

  // Validate project exists
  if (!(await validateProjectExists(projectName))) {
    return res.status(404).json({
      error: "Project does not exist.",
    });
  }

  // Validate file name format
  const fileNameRegex = /^[A-Za-z0-9_.-]+$/;
  if (!fileNameRegex.test(fileName)) {
    return res.status(400).json({
      error:
        "Invalid file name. Only alphanumeric characters, underscores, hyphens, and dots are allowed.",
    });
  }

  // Check if file exists in project
  const projectDir = join(projectPath, projectName);
  const filePath = join(projectDir, fileName);

  // Verify the resolved path is within the project directory
  if (!filePath.startsWith(projectDir)) {
    return res.status(400).json({
      error:
        "Invalid file path. File cannot be created outside the project directory.",
    });
  }

  try {
    await fs.access(filePath);
  } catch {
    return res.status(404).json({
      error: "File does not exist in the project.",
    });
  }

  // Compile the C file using Firejail
  const { exec } = await import("child_process");
  
  try {
    // Execute compilation with Firejail
    // Use a more compatible approach - change directory and run without complex whitelisting
    const compileCommand = `cd "${projectDir}" && firejail --profile=/etc/firejail/compile-c.profile gcc -o "${fileName.replace(".c", "")}" "${fileName}"`;
    
    const { stdout, stderr } = await new Promise((resolve, reject) => {
      exec(compileCommand, { timeout: 30000 }, (error, stdout, stderr) => {
        if (error) {
          // For compilation errors, we still want to return the result
          // The error might be due to compilation failing, but we still get stdout/stderr
          if (stdout || stderr) {
            resolve({ stdout, stderr });
          } else {
            reject(error);
          }
        } else {
          resolve({ stdout, stderr });
        }
      });
    });

    // Check if compilation was successful
    // Firejail outputs initialization info to stderr, so we need to be more careful
    // If stderr contains only Firejail initialization messages, consider it successful
    const firejailMessages = [
      "Reading profile",
      "Parent pid",
      "Child process initialized",
      "Parent is shutting down"
    ];
    
    const isFirejailOnlyOutput = stderr && 
      firejailMessages.every(msg => stderr.includes(msg)) && 
      stderr.split('\n').filter(line => line.trim()).length <= firejailMessages.length;
    
    // If there are actual compilation errors (not just Firejail messages) OR 
    // if there are other non-Firejail messages in stderr, consider it a failure
    const hasActualErrors = stderr && 
      (!isFirejailOnlyOutput || stderr.split('\n').filter(line => line.trim()).length > firejailMessages.length);
    
    if (hasActualErrors) {
      // Compilation had errors (or Firejail had issues)
      return res.status(200).json({
        success: false,
        stdout: stdout,
        stderr: stderr,
      });
    } else {
      // Compilation successful - check if output file was created
      const outputFile = join(projectDir, fileName.replace(".c", ""));
      try {
        await fs.access(outputFile);
        // If we get here, the file was created successfully
        return res.status(200).json({
          success: true,
          stdout: stdout,
          stderr: stderr,
        });
      } catch {
        // File was not created, but no error was thrown - this is unusual
        return res.status(200).json({
          success: false,
          stdout: stdout,
          stderr: "Compilation completed but output file not created",
        });
      }
    }
  } catch (error) {
    // Handle compilation errors
    return res.status(500).json({
      error: "Compilation failed.",
      message: error.message,
    });
  }
});

app.listen(5000, async () => {
  console.log("We work on port 5000!!");

  // Create projects folder if able, and not exists;
  try {
    await fs.access(projectPath, fs.constants.F_OK);
  } catch {
    try {
      await fs.mkdir(projectPath, { recursive: true });
    } catch {
      throw new Error("Can't create the projects directory.");
    }
  }
});
