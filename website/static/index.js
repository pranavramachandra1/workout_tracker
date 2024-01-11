function deleteNote(noteId) {
    fetch("/delete-note", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId }),
      headers: {
        'Content-Type': 'application/json'
      },
    }).then((_res) => {
      window.location.href = "/";
    });
  }


// function deleteNote(noteId) {
//     console.log("Deleting note with ID:", noteId);  // Log the note ID

//     fetch("/delete-note", {
//         method: "POST",
//         body: JSON.stringify({ noteId: noteId }),
//         headers: {
//             'Content-Type': 'application/json'
//         },
//     }).then((response) => {
//         console.log("Server response:", response);  // Log the response object

//         if (response.ok) {
//             console.log("Deletion successful, reloading page.");
//             window.location.href = "/";
//         } else {
//             console.error("Deletion failed with status:", response.status);  // Log an error if not successful
//         }
//     }).catch((error) => {
//         console.error("Error during fetch:", error);  // Log any fetch errors
//     });
// }
