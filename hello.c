#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Enumeration for greeting types
typedef enum {
    GREETING_HELLO,
    GREETING_HI,
    GREETING_HEY
} GreetingType;

// Structure to hold user information
typedef struct {
    char *name;
    int id;
    GreetingType greeting;
} User;

// Function to create a new user
User* create_user(const char *name, int id, GreetingType greeting) {
    User *user = (User *)malloc(sizeof(User));
    if (!user) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(EXIT_FAILURE);
    }
    user->name = strdup(name);
    user->id = id;
    user->greeting = greeting;
    return user;
}

// Function to free user memory
void free_user(User *user) {
    if (user) {
        free(user->name);
        free(user);
    }
}

// Function to get greeting string
const char* get_greeting(GreetingType type) {
    switch (type) {
        case GREETING_HELLO: return "Hello";
        case GREETING_HI: return "Hi";
        case GREETING_HEY: return "Hey";
        default: return "Greetings";
    }
}

// Function pointer type for greeting functions
typedef void (*GreetFunc)(const User *);

// Function to greet a user
void greet_user(const User *user) {
    printf("%s, %s! Your ID is %d.\n", get_greeting(user->greeting), user->name, user->id);
}

// Main function
int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <name>\n", argv[0]);
        return EXIT_FAILURE;
    }

    // Create a user with the provided name
    User *user = create_user(argv[1], 1001, GREETING_HELLO);

    // Function pointer to greeting function
    GreetFunc greeter = greet_user;

    // Greet the user
    greeter(user);

    // Clean up
    free_user(user);

    return EXIT_SUCCESS;
}
