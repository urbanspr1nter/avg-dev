#include <stdio.h>
#include <string.h>

char tracks[][80] = {
    "I left my heart in Harvard Med School",
    "Newark, Newark - a wonderful town",
    "Dancing with a Dork",
    "From here to maternity",
    "The girl from Iwo Jima",
};

int main(int argc, char* argv[]) {
    // Given a tracks list
    // Ask the user which track she is looking for
    // Get that input and use it to search through all tracks
    //  -> loops?
    // Display any matches. (when input occurs within the track string)
    //  -> hint: strstr() maybe?

    char input[80];
    
    printf("What is your song?\n");

    if (fgets(input, 80, stdin) == NULL) {
        printf("Something bad happened...\n");
        return 1;
    }

    char* new_line_occ = strchr(input, '\n');
    if (new_line_occ != NULL) {
        *new_line_occ = '\0';
    }

    for (int i = 0; i < 5; i++) {
        char* curr_track = tracks[i];

        // use strstr() to check if input occurs in curr_track
        char* occurrence = strcasestr(curr_track, input);

        if (occurrence != NULL) {
            printf("%s\n", curr_track);
        }
    }

    return 0;
}