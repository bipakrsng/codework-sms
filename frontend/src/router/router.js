import { createRouter, createWebHashHistory } from 'vue-router'

import login from '@/components/login.vue'
import { decodeToken, logoutUser} from '@/utils/auth';

import AdminDashboard from '@/components/AdminDashboard.vue'
import StudentDashboard from '@/components/StudentDashboard.vue'
import TeacherDashboard from '@/components/TeacherDashboard.vue'
import ParentDashboard from '@/components/ParentDashboard.vue'

import AddClass from '@/components/AddClass.vue'
import Classes from '@/components/Classes.vue'
import ClassUpdate from '@/components/ClassUpdate.vue'

import Session from '@/components/Session.vue'
import SessionAdd from '@/components/SessionAdd.vue'
import SessionUpdate from '@/components/SessionUpdate.vue'

import Student from '@/components/Student.vue'
import StudentAdd from '@/components/StudentAdd.vue'
import StudentUpdate from '@/components/StudentUpdate.vue'

import Teacher from '@/components/Teacher.vue'
import TeacherAdd from '@/components/TeacherAdd.vue'
import TeacherUpdate from '@/components/TeacherUpdate.vue'

import TimetableShow from '@/components/TimetableShow.vue'  
import TimetableCreate from '@/components/TimetableCreate.vue'

import Subject from '@/components/Subject.vue'
import SubjectAdd from '@/components/SubjectAdd.vue'

import GradeFetchers from '@/components/GradeFetcher.vue';
import GradeManagers from '@/components/GradeManager.vue';

import StudentFee from '@/components/StudentFee.vue';
import FeeCreate from '@/components/FeeCreate.vue';

import FaceRegister from '@/components/FaceRegister.vue';

import Message from '@/components/Message.vue';

import MarkAttendance from '@/components/MarkAttendance.vue';

import Pagenotfound from '@/components/Pagenotfound.vue';

import Attendance from '@/components/Attendance.vue';

import AssignSubject from '@/components/AssignSubject.vue';
// 
async function isAuthenticated1() {
  const user = decodeToken();

  //const res = await fetch()
  if (!user) {return false};
  // return user?.role[0]
  try{
    const res = await fetch(`/api/check_status/${user.user_id}`,{
      headers:{
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    const data = await res.json();

    if(!data.active){
      localStorage.removeItem('token');
      return null;
    }
    console.log(user.role[0])
    return user.role[0];
  }
  catch(err){
    localStorage.removeItem('token')
    return false;
  }
  
  
};

const adminGuard = async (to, from, next) => {
  if (await isAuthenticated1() === 'admin') {
    next(); // allow
  } else {
    
    next('/'); // redirect to login
  }
};

const studentGuard = async(to, from, next) => {
  if (await isAuthenticated1() === 'student') {
    next(); // allow
  } else {
    logoutUser()
    next('/'); // redirect to login
  }
};

const teacherGuard = async (to, from, next) => {
  if (await isAuthenticated1() === 'teacher') {
    next(); // allow
  }
  else {
    logoutUser()
    next('/'); // redirect to login
  }
};

const allguard = async (to, from, next) => {
  if (await isAuthenticated1() === 'admin' || await isAuthenticated1() === 'teacher' || await isAuthenticated1() === 'student' || await isAuthenticated1() === 'parent') {
    next(); // allow    
  } else {
    logoutUser()
    next('/'); // redirect to login
  }
};


const parentGuard = async(to, from, next) => {
  if (await isAuthenticated1() === 'parent') {
    next(); // allow
  } else {
    logoutUser()
    next('/'); // redirect to login
  }
};

const teacheradminGuard = async (to, from, next) => {
  if (await isAuthenticated1() === 'teacher' || await isAuthenticated1() === 'admin') {
    next(); // allow  
  } else {
    next('/'); // redirect to login 
  }
};

function hasValidToken() {
  const user = decodeToken();
  if (!user) return null;  // no token or invalid
  return user.role[0];     // role from decoded token
}



const routes = [
{
  path: '/',
  name: 'login',
  component: login,
  beforeEnter: (to, from, next) => {
    const role = hasValidToken();

    if (role === "admin") return next("/admin-dashboard");
    if (role === "student") return next("/student-dashboard");
    if (role === "teacher") return next("/teacher-dashboard");
    if (role === "parent") return next("/parent-dashboard");

    next(); // if no valid token, allow login page
  }
},


  { path: '/admin-dashboard', component: AdminDashboard, beforeEnter: adminGuard },
  { path: '/student-dashboard', component: StudentDashboard, beforeEnter: studentGuard },
  { path: '/teacher-dashboard', component: TeacherDashboard, beforeEnter: teacherGuard },
  { path: '/parent-dashboard', component: ParentDashboard, beforeEnter: parentGuard },

  { path: '/add-class', component: AddClass, beforeEnter: adminGuard },
  { path: '/getclasses', component: Classes, beforeEnter: adminGuard },
  { path: '/update-class/:id', component: ClassUpdate, props: true, beforeEnter: adminGuard },

  { path: '/getSession', component: Session, beforeEnter: adminGuard },
  { path: '/addSession', component: SessionAdd, name: 'CreateSession', beforeEnter: adminGuard },
  { path: '/updateSession', component: SessionUpdate, name: 'UpdateSession', beforeEnter: adminGuard },

  { path: '/getStudents', component: Student, beforeEnter: adminGuard },
  { path: '/createStudent', component: StudentAdd, beforeEnter: adminGuard },
  { path: '/updateStudent/:id', component: StudentUpdate, props: true, beforeEnter: adminGuard },

  { path: '/getTeacher', component: Teacher, beforeEnter: adminGuard },
  { path: '/createTeacher', component: TeacherAdd, beforeEnter: adminGuard },
  { path: '/updateTeacher/:id', component: TeacherUpdate, props: true, beforeEnter: adminGuard },

  { path: '/timetable/:id', component: TimetableShow, props: true, beforeEnter: adminGuard },
  { path: '/createTimetable', component: TimetableCreate, beforeEnter: adminGuard },
  { path: '/timetable/update/:id', component: TimetableCreate, props: true, beforeEnter: adminGuard },

  { path: '/getSubject', component: Subject, beforeEnter: adminGuard },
  { path: '/subjects/create', component: SubjectAdd, beforeEnter: adminGuard },
  { path: '/subjects/update/:id', component: SubjectAdd, props: true, beforeEnter: adminGuard },

  {path: '/grades/fetch/:student_id/:class_id', component: GradeFetchers,name:'GradeFetcher', beforeEnter: adminGuard},
  {path: '/grades/manage/:student_id/:class_id', component: GradeManagers, name:'GradeManager',beforeEnter: adminGuard},

  {path: '/student/fee/:student_id', component: StudentFee, name: 'StudentFee', beforeEnter: adminGuard},
  {path: '/fee/create/:student_id', component: FeeCreate, name: 'FeeCreate', beforeEnter: adminGuard},


  {path: '/face-register', component: FaceRegister, name: 'FaceRegister'},

  {path: '/message', component: Message, name: 'Message', beforeEnter: allguard},

  {path: '/mark_attendance', component: MarkAttendance, name: 'MarkAttendance', beforeEnter: teacheradminGuard},

  {path: '/attendance', component: Attendance, name: 'Attendance', props:true, beforeEnter: teacheradminGuard},
  {path: '/assign-subject', component: AssignSubject, name: 'AssignSubject', beforeEnter: adminGuard},

  // catch-all
  { path: '/:pathMatch(.*)*', component: Pagenotfound, beforeEnter:allguard}
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});
// router.beforeEach((to, from, next) => {
//   const role = isAuthenticated1();
//   console.log(role)

//   if (to.path === "/") {
//     if (role === "admin") return next("/admin-dashboard");
//     if (role === "student") return next("/student-dashboard");
//     if (role === "teacher") return next("/teacher-dashboard");
//     if (role === "parent") return next("/parent-dashboard");
//   }

//   next();
// });

export default router;
