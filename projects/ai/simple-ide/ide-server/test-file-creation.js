#!/usr/bin/env node

import fetch from "node-fetch";

async function testFileCreation() {
  const projectName = "my_c_project";
  const fileName = "hello.c";
  const content = `#include <stdio.h>
int main() {
  printf("Hello World\\n");
  return 0;
}`;

  const requestBody = {
    fileName: fileName,
    content: content,
  };

  try {
    const response = await fetch(
      `http://localhost:5000/api/projects/${projectName}/file`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      }
    );

    const result = await response.json();
    console.log("Response:", result);

    if (response.ok) {
      console.log("✅ File creation successful!");
    } else {
      console.log("❌ File creation failed:", result.error);
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

testFileCreation();
