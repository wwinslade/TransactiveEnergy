#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <jansson.h>
#include <mysql.h>
#include <wiringPi.h>

main(){
	char *host = "10.128.57.33";
	char *username= "pi";
	char *password = "sd2015";
	char *dbname = "test";
	MYSQL *conn = mysql_init(NULL);
	if(mysql_real_connect(conn,host,username,password,dbname,0,NULL,0)==NULL){
	printf("MSQL: connection failed");
	fprintf(stderr,"%s\n", mysql_error(conn));
	exit(1);
	}
	else printf ("MSQL: connection successful\n");
	
	if (mysql_query(conn,"SELECT applianceID FROM userSettings")){
	printf("Query failed\n");
	exit(1);
	}
	else printf("Query successful\n");
	MYSQL_RES *mysqlResult = mysql_store_result(conn);
	int numRow = mysql_num_rows(mysqlResult);
	int numField = mysql_num_fields(mysqlResult);
	printf("Number of rows is %i\n",numRow);
	MYSQL_ROW row = mysql_fetch_row(mysqlResult);
	while(row!=NULL){
	printf("%s \n",row[0]);}
	mysql_free_result(mysqlResult);
	mysql_close(conn);
}
