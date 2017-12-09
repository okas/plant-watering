<template>
<aside>
    <section>
        <h4>Interests...</h4>
        <ul>
            <li><a href="#">Show tank</a></li>
            <li><a href="#">Water statistics</a></li>
            <li><router-link :to="{name: 'plantmanager'}">
                Manage service
            </router-link></li>
        </ul>
    </section>
</aside>
</template>

<script>
export default { name: 'plan-aside' }
</script>

<style scoped>
aside {
    float : left;
    width : 150px;
    margin-right: 20px;
    margin-bottom : 15px;
    background-color : #D0D0D0 ;
    padding : 5px;
    border : 1px solid #A8A8A8;
}
ul {
    list-style-type: none;
    padding: 0;
}
section * {
    text-align: left;
}
</style>
