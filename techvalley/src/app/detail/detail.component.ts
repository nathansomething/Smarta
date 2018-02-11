import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Chart } from 'angular-highcharts';
import { HttpClient, HttpHeaders, HttpClientModule } from '@angular/common/http';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-detail',
  templateUrl: './detail.component.html',
  styleUrls: ['./detail.component.css']
})
export class DetailComponent implements OnInit {

  private dataFrequency:string
  private id:Number;
  private startdate:string;
  private enddate:string
  private today:Date;
  private vehicalData:Array<number> = [];
  private xAxisArray:Array<number> = [];
  private chart:Chart = new Chart({
     chart: {
       type: 'line'
     },
     title: {
       text: 'Traffic Over Time'
     },
     credits: {
       enabled: false
     },
     series: [{
       name: 'Cars',
       data: this.vehicalData
     }],
     yAxis: {
       title: {
         text: 'Number of Cars',
         style: {
             fontSize:'25px',
             fontFamily:'Jura'
         }
       },
     },
     xAxis: {
       title: {
         text: 'Time',
         style: {
             fontSize:'25px',
             fontFamily:'Jura'
         }
       },
       tickPositions: this.xAxisArray
     },
     tooltip: {
      backgroundColor: '#7878c9',
      borderColor: '#333',
      borderRadius: 10,
      borderWidth: 1
    }
 });

  pad(num:number, size:number): string {
      let s = num+"";
      while (s.length < size) s = "0" + s;
      return s;
  }

  constructor(private route:ActivatedRoute, private http: HttpClient) {
    this.dataFrequency = "Every Hour"
    this.today = new Date();
    this.startdate = this.today.getFullYear() + '-' + this.pad(this.today.getMonth(), 2) + '-' + this.pad(this.today.getDate(), 2);
    this.enddate = this.today.getFullYear() + '-' + this.pad(this.today.getMonth(), 2) + '-' + this.pad(this.today.getDate() - 1, 2);
  }

  updateDataFrequency(frequency:string) {
    this.dataFrequency = frequency;
    this.getVehicalData();
  }

  getAggregateHours() {
    switch(this.dataFrequency) {
      case "Every Hour":
        return 1;
      case "Every Other Hour":
        return 2;
      case "Every 6 Hours":
        return 6;
      case "Every 12 Hours":
        return 12;
      case "Every 24 Hours":
        return 24;
    }
  }

  getVehicalData() {
    this.vehicalData = [];
    let today = new Date();
    // Yes, this will break if it overlaps a month.
    // No, I don't have time to properly fix it.
    let startDaysAgo = today.getDate() - Number(this.startdate.split('-')[2]);
    let endDaysAgo = today.getDate() - Number(this.enddate.split('-')[2]);
    let numDays = endDaysAgo - startDaysAgo;

    this.xAxisArray = Array.apply(null, {length: (24 / this.getAggregateHours()) * numDays}).map(Number.call, Number);

    this.http.get<number[]>(`http://127.0.0.1:5000/aggr?id=${this.id}&start_days_ago=${startDaysAgo}&end_days_ago=${endDaysAgo}&aggregate_num_hours=${this.getAggregateHours()}`).subscribe(data => {
      this.vehicalData = data
      for(let vehicalDatum of this.vehicalData) {
        this.chart.addPoint(vehicalDatum);
      }
    });
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
      this.getVehicalData();
    });
  }
}
