rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own data
    match /users/{userId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.uid == userId;
      
      // Subcollections
      match /stargateResults/{resultId} {
        allow read, write: if request.auth != null && request.auth.uid == userId;
      }
    }
    
    // Pods - authenticated users can read all, write if member
    match /pods/{podId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null;
      allow update: if request.auth != null && 
        request.auth.uid in resource.data.members.map(member => member.uid);
      
      // Pod messages
      match /messages/{messageId} {
        allow read: if request.auth != null;
        allow write: if request.auth != null;
      }
    }
    
    // Help tickets - users can read own, teachers can read all
    match /helpTickets/{ticketId} {
      allow read: if request.auth != null && 
        (request.auth.uid == resource.data.studentId || 
         get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'teacher');
      allow create: if request.auth != null;
      allow update: if request.auth != null && 
        (request.auth.uid == resource.data.studentId || 
         get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'teacher');
    }
    
    // Tournaments - all authenticated users can read
    match /tournaments/{tournamentId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'teacher';
      allow update: if request.auth != null && request.auth.uid in resource.data.participants.map(p => p.uid);
    }
    
    // Daily challenges - read only
    match /dailyChallenges/{date} {
      allow read: if request.auth != null;
      allow write: if false; // Only server can write
    }
  }
}