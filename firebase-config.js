import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { getDatabase, ref, push } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js";

const firebaseConfig = {
  apiKey: "AIzaSyDp6IB_ZndLgMWamLzThb5EBqClYSQf2LM",
  authDomain: "lozano-1690859356322.firebaseapp.com",
  databaseURL: "https://lozano-1690859356322-default-rtdb.firebaseio.com",
  projectId: "lozano-1690859356322",
  storageBucket: "lozano-1690859356322.firebasestorage.app",
  messagingSenderId: "562516890895",
  appId: "1:562516890895:web:ba63485fe983cf037dda7a"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getDatabase(app);
export { signInWithEmailAndPassword, ref, push };