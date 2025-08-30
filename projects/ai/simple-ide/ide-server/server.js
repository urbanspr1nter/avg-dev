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
