#!/usr/bin/env node

// Simple test script to verify GET file endpoint works
import fetch from "node-fetch";

async function testGetFile() {
  const projectName = "my_c_project";
  const fileName = "hello.c";

  try {
    console.log("Testing GET file endpoint...");
    console.log(`Getting file: ${fileName} from project: ${projectName}`);

    const response = await fetch(
      `http://localhost:5000/api/projects/${projectName}/file/${fileName}`,
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
      console.log("✅ GET request successful!");
      console.log("File contents:", result.data);
    } else {
      console.log("❌ GET request failed:", result.error);
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

// Run the test
testGetFile();
