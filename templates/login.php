


<?php
// ouvrir une connexion vers mysql ici
// Sous WAMP (Windows)
//$bdd = new PDO('mysql:host=localhost;dbname=test;charset=utf8', 'root', '');

// Sous MAMP (Mac)
$bdd = new PDO('mysql:host=localhost;dbname=test;charset=utf8', 'root', 'root');
?>
<?php
// ouvrir une connexion vers mysql ici avec le serveur d'hebergement lorsqu'on mettra le site vers le web
//$bdd = new PDO('mysql:host=sql.hebergeur.com;dbname=mabase;charset=utf8', 'pierre.durand', 's3cr3t');
?>
 
<?
if(isset($_POST) && !empty($_POST['login']) && !empty($_POST['pass'])) {
  extract($_POST);
  // on recupère le password de la table qui correspond au login du visiteur
  $sql = "select pwd from tbl_user where login='".$login."'";
  $req = mysql_query($sql) or die('Erreur SQL !<br>'.$sql.'<br>'.mysql_error());

  $data = mysql_fetch_assoc($req);

  if($data['pwd'] != $pass) {
    echo '<p>Mauvais login / password. Merci de recommencer</p>';
    include('login.htm'); // On inclut le formulaire d'identification
    exit;
  }
  else {
    session_start();
    $_SESSION['login'] = $login;
    
    echo 'Vous etes bien logué';
    // ici vous pouvez afficher un lien pour renvoyer
    // vers la page d'accueil de votre espace membres 
  }    
}
else {
  echo '<p>Vous avez oublié de remplir un champ.</p>';
   include('login.htm'); // On inclut le formulaire d'identification
   exit;
}


?>