#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <jansson.h>
#include <mysql.h>
#include <wiringPi.h>

int on_pins[4] = {0, 2, 3, 7};
int on_pins_length = 4;
int off_pins[4] = {21, 23, 24, 22};
int off_pins_length = 4;

void init_pins();
void turn_pin_on_off(int pin);

int main(){
  wiringPiSetup();
  
  init_pins();

  MYSQL *conn = mysql_init(NULL);
  if(mysql_real_connect(conn, "10.128.57.30", "pi", "sd2015", "test",0, NULL, 0) == NULL){
    printf("MYSQL: Connection failed\n");
    return 1;
  }
  printf("MYSQL: Connection successful\n");
  
  int numAppliances = -1;
  int *onOffStates = NULL;
  while(1){
    char *query = "SELECT applianceID, state FROM userSettings ORDER BY applianceID;";
    int mysqlStatus = mysql_query(conn, query);

    if(mysqlStatus){
        printf("MYSQL: Query Unsuccessful\n");
      return 1;
    }
    else{
       printf("MYSQL: Query Successful\n");
    }

    MYSQL_RES *mysqlResult = mysql_store_result(conn);

    int numRows = mysql_num_rows(mysqlResult);
    int numFields = mysql_field_count(conn); 
    printf("MYSQL: Queried %i rows with %i fields each\n", numRows, numFields);
    
    if(numAppliances == -1){
      int j;
      onOffStates = malloc(sizeof(int) * numRows);
      for(j = 0; j < numRows; j++){
        onOffStates[j] = -1;
      }
      numAppliances = numRows;
    }
    else if(numAppliances != numRows){
      int j;
      free(onOffStates);
      onOffStates = malloc(sizeof(int) * numRows);
      for(j = 0; j < numRows; j++){
        onOffStates[j] = -1;
      }
      numAppliances = numRows;
    }

    MYSQL_ROW mysqlRow;
    int i = 0;
    while(mysqlRow = mysql_fetch_row(mysqlResult)){
      // printf(mysqlRow[0]);
      // printf("\n");
      if(mysqlRow[1][0] == '1'){ 
        if(onOffStates[i] != 1){
          // printf("Turning appliance %d on\n", i);
          turn_pin_on_off(on_pins[i]);
          onOffStates[i] = 1;
        }
        else{
          // printf("Appliance %d is already on, skipping\n", i);
        }
      }
      else{ 
        if(onOffStates[i] != 0){
          // printf("Turning appliance %d off\n", i);
          turn_pin_on_off(off_pins[i]);
          onOffStates[i] = 0;
        }
        else{
          // printf("Appliance %d is already off, skipping\n", i);
        }
      }
      i++;
    }
    mysql_free_result(mysqlResult);
    delay(50);
  }
  mysql_close(conn);
}

void init_pins(){
  int i;
  for(i = 0; i < on_pins_length; i++){
    pinMode(on_pins[i], OUTPUT);
    digitalWrite(on_pins[i], LOW);
  }
  for(i = 0; i < off_pins_length; i++){
    pinMode(off_pins[i], OUTPUT);
    digitalWrite(off_pins[i], LOW);
  }
}

void turn_pin_on_off(int pin){
  pinMode(pin, OUTPUT);
  digitalWrite(pin, HIGH);
  delay(100); 
  digitalWrite(pin, LOW);	
}
