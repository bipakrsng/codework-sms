<template>
    <nav-bar></nav-bar>
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h3>Sessions</h3>
            <button class="btn btn-primary" @click="openCreateSession">
                Create New Session
            </button>
        </div>
        <table class="table table-bordered table-striped">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Start Date</th>
                    <th>End date</th>
                    <th>Active</th>
                    <th>Action</th>
                </tr>

            </thead>
            <tbody>
                <tr v-for="session in sessions" :key="session.id">
                    <td>{{ session.id }}</td>
                    <td>{{ session.name }}</td>
                    <td>{{ formatDate(session.start_date) }}</td>
                    <td>{{ formatDate(session.end_date) }}</td>
                    <td> 
                        <span class="badge" :class="session.is_active?'bg-success':'bg-danger'">{{ session.is_active ?'Active' : 'Inactive' }}</span>
                    </td>

                    <td>
                        <button class="btn btn-sm btn-info me-2" @click="UpdateSession(session)">Update</button>
                    
                        <button class="btn btn-sm btn-danger" @click="deleteSession(session.id)">Delete</button>
                    </td>

                </tr>
            </tbody>
            
        </table>

        <div v-if="loading" class="text-center mt-3">
            <div class="spinner-border" role="status"></div>
        </div>
    </div>
</template>
<script>
import { useSessionStore } from '@/store/userStore';
export default{
    name : "SessionTable",
    data(){
        return{
            sessions:[],
            loading:false,
        }
    },
    methods:{
        async fetchSessions(){
            try{
                this.loading=true;
                const res = await fetch ('/api/get_sessions',{
                    method:'GET',
                    headers:{
                        'Content-Type':'application/json',
                        "Authorization": "Bearer " + localStorage.getItem('token')
                    }
                });
                if (!res.ok) throw new Error("Failed to fetch sessions");
                this.sessions = await res.json();
            }
            catch(err){
                console.error(err)
                alert("Error fetching sessions");
            }
            finally{
                this.loading=false;
            }
        },

        formatDate(dateStr){
            return new Date(dateStr).toLocaleDateString();
        },

        openCreateSession(){
            this.$router.push({name:'CreateSession'})
        },
        UpdateSession(session){
            const store = useSessionStore();
            store.currentSession = session;
            this.$router.push({name:'UpdateSession'})
        },

        async deleteSession(id){
            if (!confirm("Are you sure you want to dleete this session?")) return;
            try{
                const res = await fetch(`/api/delete_session/${id}`,{
                    method:'DELETE',
                    headers:{
                        'Content-Type':'application/json',
                        "Authorization": "Bearer " + localStorage.getItem('token')
                        }

                });
                if (!res.ok) throw new Error("Failed to delete session");
                this.sessions = this.sessions.filter(s => s.id !== id);
            }
            catch(err){
                console.error(err);
                alert("Error deleting session");
            
            }
        }
    },
    mounted(){
        this.fetchSessions();
    }
}
</script>