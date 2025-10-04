#!/usr/bin/env node

// Test script to verify the compile endpoint works
import fetch from "node-fetch";

async function testCompileEndpoint() {
  const projectName = "my_c_project";
  const fileName = "hello.c";

  try {
    console.log("Testing POST /api/projects/:projectName/compile/:fileName endpoint...");
    console.log(`Compiling file: ${fileName} in project: ${projectName}`);

    const response = await fetch(
      `http://localhost:5000/api/projects/${projectName}/compile/${fileName}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    const result = await response.json();
    console.log("Response Status:", response.status);
    console.log("Response Body:", JSON.stringify(result, null, 2));

    if (response.ok) {
      console.log("✅ Compile request successful!");
      if (result.success) {
        console.log("✅ Compilation successful!");
        console.log("stdout:", result.stdout);
      } else {
        console.log("❌ Compilation failed!");
        console.log("stderr:", result.stderr);
      }
    } else {
      console.log("❌ Compile request failed:", result.error);
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

// Run the test
testCompileEndpoint();
