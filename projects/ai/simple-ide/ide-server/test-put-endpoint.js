#!/usr/bin/env node

import fetch from "node-fetch";

async function testPutEndpoint() {
  const projectName = "my_c_project";
  const fileName = "hello.c";
  const updatedContent = `#include <stdio.h>
int main() {
  printf("File updated successfully!\\n");
  return 0;
}`;

  const requestBody = {
    fileName: fileName,
    content: updatedContent,
  };

  try {
    console.log("Testing PUT endpoint...");
    console.log(`Updating file: ${fileName} in project: ${projectName}`);

    const response = await fetch(
      `http://localhost:5000/api/projects/${projectName}/file/${fileName}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      }
    );

    const result = await response.json();
    console.log("Response Status:", response.status);
    console.log("Response Body:", result);

    if (response.ok) {
      console.log("✅ PUT request successful!");
    } else {
      console.log("❌ PUT request failed:", result.error);
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

// Run the test
testPutEndpoint();
