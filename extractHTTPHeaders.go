//This is the code for extracting HTTP Response headers for a 
//given url and printing them onto the console

package main

import (
        "fmt"
        "net/http"
)

func main() {
resp, err := http.Get("http://www.facebook.com/")

//Check for error
if err != nil {
    fmt.Printf("Error sending request")
}

//Iterate through each (key,value) pair in response's Header
for key, value := range resp.Header {
    fmt.Println("Key:", key, "Value:", value)
}

}
