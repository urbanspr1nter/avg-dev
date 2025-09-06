#!/usr/bin/env node

// Test script to verify listing endpoints work correctly
import fetch from "node-fetch";

async function testListProjects() {
  try {
    console.log("Testing GET /api/projects endpoint...");

    const response = await fetch(`http://localhost:5000/api/projects`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const result = await response.json();
    console.log("Response Status:", response.status);
    console.log("Response Body:", JSON.stringify(result, null, 2));

    if (response.ok) {
      console.log("✅ List projects request successful!");
      console.log("Projects found:", result.projects);
    } else {
      console.log("❌ List projects request failed:", result.error);
    }
  } catch (error) {
    console.error("Error testing list projects:", error);
  }
}

async function testListProjectFiles() {
  const projectName = "my_c_project";

  try {
    console.log("\nTesting GET /api/projects/:projectName/files endpoint...");
    console.log(`Listing files in project: ${projectName}`);

    const response = await fetch(
      `http://localhost:5000/api/projects/${projectName}/files`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    const result = await response.json();
    console.log("Response Status:", response.status);
    console.log("Response Body:", JSON.stringify(result, null, 2));

    if (response.ok) {
      console.log("✅ List files request successful!");
      console.log("Files found:", result.files.length);
      result.files.forEach((file) => {
        console.log(`  - ${file.name} (${file.size} bytes)`);
      });
    } else {
      console.log("❌ List files request failed:", result.error);
    }
  } catch (error) {
    console.error("Error testing list files:", error);
  }
}

async function runAllTests() {
  console.log("Running listing endpoint tests...\n");

  await testListProjects();
  await testListProjectFiles();

  console.log("\nTest execution completed.");
}

// Run all tests
runAllTests();
